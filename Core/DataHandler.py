import asyncio
import time

from Data.ListCoins import ListCoins
from exchange.BybitApi import BybitApi
from exchange.CoinWApi import CoinWApi
from exchange.OkxApi import OkxApi
from collections import Counter

class DataHandler:
    def __init__(self, name = "DataHandler"):
        self.name = name
        self.ListCoins = ListCoins()

    async def get_common_pairs_and_data(self, apis):
        """
        Функция берет данные для всех монет котировку и объем
        :param apis: список бирж
        :return: список общих монетных пар и словарь с данными с котировками и объемом
        """
        # Создаем список задач для каждого API, чтобы получить данные асинхронно
        tasks = [api.get_coins_price_vol() for api in apis]
        # Запускаем все задачи асинхронно и ждем их завершения
        all_data = await asyncio.gather(*tasks)
        # Получаем список всех пар из всех словарей
        all_pairs = [pair for data in all_data for pair in data.keys()]
        # Считаем количество каждой пары
        pair_counts = Counter(all_pairs)
        # Находим общие пары, которые есть в каждом словаре
        # Это те пары, количество которых равно количеству API
        common_pairs = [pair for pair, count in pair_counts.items() if count == len(apis)]

        return common_pairs, all_data
    async def get_exchange_data(self, data1, data2, api1, api2):
        """
            Функция обходит все значения двух словарей и вычисляет разницу котировок.
            :param data1: Данные первой биржи
            :param data2: Данные второй биржи
            :param api1: Имя первой биржи
            :param api2: Имя второй биржи
            :return: Вернет словарб с данными, где будет добавлен ключ с разницой в процентах
        """
        # Создаем словарь для хранения результата
        result = {}
        # Обходим все пары в данных
        for pair in data1.keys():
            # Если пара есть в обоих словарях
            if pair in data2:
                # Вычисляем разницу в котировках
                a = float(data1[pair]['price'])
                b = float(data2[pair]['price'])
                dif = ((a - b) / a) * 100
                # Добавляем данные в словарь, если разница в процентах находится в нужном диапазоне
                if 0.8 < dif <= 2.5:
                    result[pair] = {
                        'data': {
                            api1.name: data1[pair],
                            api2.name: data2[pair]
                        },
                        'dif': round(dif, 4)
                    }
        return result
    async def get_all_exchange_data(self, apis):
        """
        Функция принимает словарь с биржами и преобразует его в словарь с Биржа-Биржа -> монета -> Биржа ....
        :param apis: список бирж
        :return: словарь с данными и отношением и разницой.
        """
        # Получаем общий список монетных пар и данные от всех API
        common_pairs, all_data = await self.get_common_pairs_and_data(apis)
        # Создаем словарь для хранения результатов
        results = {}
        # Обходим все пары API
        for i in range(len(apis)):
            for j in range(i + 1, len(apis)):
                # Получаем данные для этой пары API
                data1 = {pair: all_data[i][pair] for pair in common_pairs if pair in all_data[i]}
                data2 = {pair: all_data[j][pair] for pair in common_pairs if pair in all_data[j]}
                result = await self.get_exchange_data(data1, data2, apis[i], apis[j])
                # Добавляем результат в словарь
                pair_name = f"{apis[i].name}-{apis[j].name}"
                if pair_name not in results:
                    results[pair_name] = {}
                results[pair_name].update(result)

        return results
    async def get_best_ticker(self, apis):
        """
            Функция добавляет в словарь с Биржами-монетами-... , сеть и коммисию за операцию
            :param apis: список Бирж
            :return: словарь который содержит полную информацию
        """
        # Запрашиваем все данные
        all_exchange_data = await self.get_all_exchange_data(apis)
        # Обходим все пары API
        for pair_name, pairs in all_exchange_data.items():
            # Обходим все монеты в парах
            for coin, data in pairs.items():
                # Создаем список задач для каждого API
                tasks = []
                # Добавляем список для отслеживания порядка API
                api_order = []
                # Обходим все API
                for api in apis:
                    # Если имя API есть в данных монеты
                    if api.name in data['data']:
                        onecoin = await self.ListCoins.get_first_coin(coin)
                        # Создаем задачу для получения комиссии сети для этой монеты
                        task = asyncio.create_task(api.get_network_commission(onecoin))
                        tasks.append(task)
                        # Добавляем имя API в список
                        api_order.append(api.name)
                # Запускаем все задачи асинхронно и ждем их завершения
                network_commissions = await asyncio.gather(*tasks)

                # Добавляем комиссию сети в данные монеты
                for i, api_name in enumerate(api_order):
                    # Используем api_name из списка api_order
                    if api_name in data['data'] and i < len(network_commissions):
                        data['data'][api_name]['network'] = network_commissions[i]
        return all_exchange_data


if __name__ == "__main__":

    start_time = time.time()
    async def main():
        okx = OkxApi("Okx")
        bybit = BybitApi("Bybit")
        coinw = CoinWApi("Coin W")

        ex_list = []
        ex_list.append(okx)
        ex_list.append(bybit)
        ex_list.append(coinw)

        DH = DataHandler("DH")
        await DH.ListCoins.initialize_data()

        # Получаем все данные обмена
        # all_exchange_data = await DH.get_all_exchange_data(ex_list)
        # print(all_exchange_data)

        # print(f'Все данные  : {all_exchange_data}')
        # print(f'Все уникальные данные  : {len(all_exchange_data)}')
        #

        #Добавляем данные о комиссии
        all_exchange_data2 = await DH.get_best_ticker(ex_list)
        print(f'Все данные  : {all_exchange_data2}')
        print(f'Все уникальные данные  : {len(all_exchange_data2)}')

    asyncio.run(main())

    end_time = time.time()
    print(f'Код отработал за {end_time - start_time}')



