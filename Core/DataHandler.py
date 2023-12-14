import asyncio
import sys
import time
import traceback

import TelBot.CallHandler
from Data.ListCoins import ListCoins
from exchange.GateApi import GateApi
from exchange.MexcApi import MexcApi
from exchange.BybitApi import BybitApi
from exchange.CoinWApi import CoinWApi
from exchange.OkxApi import OkxApi
from collections import Counter

class DataHandler:
    def __init__(self, name = "DataHandler"):
        # Имя класса
        self.name = name
        # Переменная, класс который содержит список монет(разбитые монетные пары)
        self.ListCoins = ListCoins()
        # Переменные хранят информацию о диапозоне фильтра
        self.max_spred = 2.5
        self.min_spred = 0.8
    def set_min_max_spred(self,min: float, max: float):
        """
            Функция устанавливает максимум и минимум диапозона , для фильтра спреда.
            :param max: максимальный процент
            :param min: минимальный процент
            :return: None
        """
        self.min_spred = min
        self.max_spred = max
    async def get_common_pairs_and_data(self, apis):
        """
        Функция берет данные для всех монет котировку и объем и находим общиее.
        :param apis: список бирж
        :return: список общих монетных пар и словарь с данными с котировками и объемом
        """
        #start_time = time.time()

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
       # print(f"ОБЩИЕ ПАРЫ = {len(common_pairs)}")
        #end_time = time.time()
        #print(f'Функция get_common_pairs_and_data отработала за {end_time - start_time}')
        return common_pairs, all_data

    async def get_exchange_data(self, data1, data2, api1, api2):
        """
            Функция обходит все значения двух словарей и вычисляет разницу котировок.
            :param data1: Данные первой биржи
            :param data2: Данные второй биржи
            :param api1: Имя первой биржи
            :param api2: Имя второй биржи
            :return: Вернет словарь с данными, где будет добавлен ключ с разницой в процентах
        """
        #start_time = time.time()
        # Создаем словарь для хранения результата
        result = {}
        try:
            # Обходим все пары в данных
            for pair in data1.keys():
                # Если пара есть в обоих словарях
                if pair in data2:
                    # Вычисляем разницу в котировках
                    a = float(data1[pair]['price'])
                    b = float(data2[pair]['price'])
                    if a != 0 and b != 0:
                        dif = ((a - b) / a) * 100
                        # Добавляем данные в словарь, если разница в процентах находится в нужном диапазоне
                        if self.min_spred < dif <= self.max_spred:
                            if a < b:
                                result[pair] = {
                                    'data': {
                                        api1.name: data1[pair],
                                        api2.name: data2[pair]
                                    },
                                    'dif': round(dif, 4)
                                }
                            else:
                                result[pair] = {
                                    'data': {
                                        api2.name: data2[pair],
                                        api1.name: data1[pair]
                                    },
                                    'dif': round(dif, 4)
                                }
                    else:
                        print(f" a == pair = {pair} datapair1 = {data1[pair]} price = {float(data1[pair]['price'])} ")
                        print(f"b == pair = {pair} datapair2 = {data2[pair]} price = {float(data2[pair]['price'])} ")
            #end_time = time.time()
            #print(f'Функция get_exchange_data отработала за {end_time - start_time}')
            # diff_counts = {}
            # for pair, info in result.items():
            #     diff = info['dif']
            #     diff = round(diff)  # Округляем до целого процента
            #     if diff not in diff_counts:
            #         diff_counts[diff] = 0
            #     diff_counts[diff] += 1
            #
            # print("Словарь с процентами разницы и количеством соответствующих пар:")
            # total_diffs = 0
            # total_pairs = 0
            # for diff, count in diff_counts.items():
            #     print(f"{diff}%: {count} pair(s)")
            #     total_diffs += 1
            #     total_pairs += count
            #
            # print(f"Общее количество процентов: {total_diffs}")
            # print(f"Общее количество пар: {total_pairs}")
            return result
        except Exception as e:
            print(f"Возникла ошибка монета = {pair} a={a}, b={b}, dif = {round(((a - b) / a)*100,4)}: {e} get_exchange_data")
            return {}
    async def get_all_exchange_data(self, apis):
        """
        Функция принимает словарь с биржами и преобразует его в словарь с Биржа-Биржа -> монета -> Биржа ....
        :param apis: список бирж
        :return: словарь с данными и отношением и разницой.
        """
        start_time = time.time()
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
                # Внимание имя словаря не соответствует порядку по цени, а лишь по перебору
                # так что при выводе информации использовать название кто первый и второй в data идет
                pair_name = f"{apis[i].name}-{apis[j].name}"
                if pair_name not in results:
                    results[pair_name] = {}
                results[pair_name].update(result)
        #end_time = time.time()
        #print(f'Функция get_all_exchange_data отработала за {end_time - start_time}')
        return results

    async def get_best_ticker(self, apis):
        #start_time = time.time()
        try:
            # Получаем данные с бирж
            all_exchange_data = await self.get_all_exchange_data(apis)
            # Обходим данные каждой биржи и их монет
            for pair_name, pairs in all_exchange_data.items():
                for coin, data in pairs.items():
                    tasks = {}
                    for api in apis:
                        # Проверяем, есть ли имя биржи в данных монеты
                        if api.name in data['data']:
                            # Создаем задачу для получения комиссии сети для этой монеты
                            coin_info = await self.ListCoins.get_first_coin(coin)
                            task = asyncio.create_task(api.get_network_commission(coin_info))
                            # print(f'API {api.name} = {api.data_network == None}')
                            tasks[api.name] = task
                    # Собираем результаты асинхронных задач
                    network_commissions = await asyncio.gather(*tasks.values())
                    # Добавляем комиссию сети в данные монеты
                    for i, api_name in enumerate(tasks.keys()):
                        if api_name in data['data']:
                            data['data'][api_name]['network'] = network_commissions[i]
           # end_time = time.time()
           # print(f'Функция get_best_ticker отработала за {end_time - start_time}')
            return all_exchange_data
        except Exception as e:
            # Обработка исключений
            print(f'Произошла ошибка метод get_best_ticker: {e}')
            return None  # Можно выбрасывать исключение или возвращать информацию об ошибке

    # Мой Вариант
    # async def get_best_ticker1(self, apis):
    #     """
    #         Функция добавляет в словарь с Биржами-монетами-... , сеть и коммисию за операцию
    #         :param apis: список Бирж
    #         :return: словарь который содержит полную информацию
    #     """
    #     start_time = time.time()
    #     # Запрашиваем все данные
    #     all_exchange_data = await self.get_all_exchange_data(apis)
    #     # Обходим все пары API
    #     for pair_name, pairs in all_exchange_data.items():
    #         # Обходим все монеты в парах
    #         for coin, data in pairs.items():
    #             # Создаем список задач для каждого API
    #             tasks = []
    #             # Добавляем список для отслеживания порядка API
    #             api_order = []
    #             # Обходим все API
    #             for api in apis:
    #                 # Если имя API есть в данных монеты
    #                 if api.name in data['data']:
    #                     onecoin = await self.ListCoins.get_first_coin(coin)
    #                     # Создаем задачу для получения комиссии сети для этой монеты
    #                     task = asyncio.create_task(api.get_network_commission(onecoin))
    #                     tasks.append(task)
    #                     # Добавляем имя API в список
    #                     api_order.append(api.name)
    #             # Запускаем все задачи асинхронно и ждем их завершения
    #             network_commissions = await asyncio.gather(*tasks)
    #
    #             # Добавляем комиссию сети в данные монеты
    #             for i, api_name in enumerate(api_order):
    #                 # Используем api_name из списка api_order
    #                 if api_name in data['data'] and i < len(network_commissions):
    #                     data['data'][api_name]['network'] = network_commissions[i]
    #     end_time = time.time()
    #     print(f'Функция get_best_ticker1 отработала за {end_time - start_time}')
    #     return all_exchange_data
    #
    # #Вариант от Старика
    # async def get_best_ticker2(self, apis):
    #     start_time = time.time()
    #     all_exchange_data = await self.get_all_exchange_data(apis)
    #     tasks = []
    #
    #     for pair_name, pairs in all_exchange_data.items():
    #         for coin, data in pairs.items():
    #             tasks_per_coin = []
    #             api_order = []
    #
    #             for api in apis:
    #                 if api.name in data['data']:
    #                     onecoin = await self.ListCoins.get_first_coin(coin)
    #                     task = asyncio.create_task(api.get_network_commission(onecoin))
    #                     tasks_per_coin.append(task)
    #                     api_order.append(api.name)
    #
    #             if tasks_per_coin:
    #                 network_commissions = await asyncio.gather(*tasks_per_coin)
    #
    #                 for i, api_name in enumerate(api_order):
    #                     if api_name in data['data'] and i < len(network_commissions):
    #                         data['data'][api_name]['network'] = network_commissions[i]
    #
    #     end_time = time.time()
    #     print(f'Функция get_best_ticker2 отработала за {end_time - start_time}')
    #     return all_exchange_data

    async def get_coin_all_exchange(self, ex_list, coin_pair):
        try:
            # Разделяем монетную пару
            onecoin = await self.ListCoins.get_first_coin(coin_pair.upper())
            twocoin = coin_pair[len(onecoin):].upper()#coin_pair.upper().split(onecoin)[1]
            #print(onecoin,twocoin)
            # Формируем переменных с монетными парами для каждой биржи
            #  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Обязательно добавь!!!!!!!!!!!!!!!
            coinw_pair = f"{onecoin}_{twocoin}".lower()
            bybit_pair = coin_pair.upper()
            okx_pair = f"{onecoin}-{twocoin}".upper()
            mexc_pair = f"{onecoin}_{twocoin}".lower()
            gateio_pair = f"{onecoin}_{twocoin}".lower()
            # Список задач.
            tasks = []
            # Проходим по списку бирж и проверяем на основе имени.
            for exchang in ex_list:
                if "Okx" in exchang.name:
                    task = asyncio.create_task(exchang.get_one_coin(okx_pair))
                    tasks.append(task)
                elif "Bybit" in exchang.name:
                    task = asyncio.create_task(exchang.get_one_coin(bybit_pair))
                    tasks.append(task)
                elif "Coin W" in exchang.name:
                    task = asyncio.create_task(exchang.get_one_coin(coinw_pair))
                    tasks.append(task)
                elif "Mexc" in exchang.name:
                    task = asyncio.create_task(exchang.get_one_coin(mexc_pair))
                    tasks.append(task)
                elif "Gate.io" in exchang.name:
                    task = asyncio.create_task(exchang.get_one_coin(gateio_pair))
                    tasks.append(task)
            # Запускаем все запросы одновременно
            results = await asyncio.gather(*tasks)

            final_results = []
            for exchang, result in zip(ex_list, results):
                result_without_first_key = {exchang.name: list(result.values())[0]}
                final_results.append(result_without_first_key)

                # Вычисляем разницу в ценах между всеми биржами
            for i in range(len(final_results)):
                exchang1 = list(final_results[i].keys())[0]
                price1 = float(final_results[i][exchang1]['price'])
                dif_dict = {}
                for j in range(len(final_results)):
                    if i != j:
                        exchang2 = list(final_results[j].keys())[0]
                        price2 = float(final_results[j][exchang2]['price'])
                        dif = ((price1 - price2) / price1) * 100
                        dif_dict[f'{exchang1} -> {exchang2}'] = format(-dif, '.5f')  # меняем знак
                final_results[i][exchang1]['dif'] = dif_dict  # добавляем dif_dict в конец словаря

            return final_results
        except Exception as e:
            print(e)

if __name__ == "__main__":

    # def trace_calls(frame, event, arg):
    #     if event != 'call':
    #         return
    #     code = frame.f_code
    #     function_name = code.co_name
    #     if function_name == 'get_coins_price_vol':
    #         print(f'Function {function_name} was called from {frame.f_back.f_code.co_name}')
    #         traceback.print_stack(frame)
    #
    #
    # sys.settrace(trace_calls)

    start_time = time.time()
    async def main():

        okx = OkxApi("Okx")
        bybit = BybitApi("Bybit")
        coinw = CoinWApi("Coin W")
        mexc = MexcApi("Mexc")
        gate = GateApi("Gate.io")

        # #  дубли для теста
        # okx2 = OkxApi("Okx2")
        # bybit2 = BybitApi("Bybit2")
        # coinw2 = CoinWApi("Coin W2")

        ex_list = []
        # ex_list.append(okx)
        #ex_list.append(bybit)

        DH = DataHandler("DH")
        await DH.ListCoins.initialize_data()

        # print("********** Тест на 2 биржах")
        # test1 = await DH.get_best_ticker(ex_list)
        #
        #ex_list.append(coinw)

        # print("********** Тест на 3 биржах")
        # test2 = await DH.get_best_ticker(ex_list)
        #await gate._load_network_commission()
        ex_list.append(mexc)
        ex_list.append(gate)



        print(f"********** Тест на _ биржах spred spisok = {ex_list} = {DH.min_spred} - {DH.max_spred}")
        test3 = await DH.get_best_ticker(ex_list)
       # print(test3)
        #newtest = await DH.get_best_ticker_for_all_pairs(ex_list)

    asyncio.run(main())

    end_time = time.time()
    print(f'Код отработал за {end_time - start_time}')

    # Добавляем данные о комиссии
    #  all_exchange_data2 = await DH.get_best_ticker(ex_list)
    #  # all_exchange_data2 = await DH.get_coin_all_exchange(ex_list, "BTCUSDT")
    #  # olol = await TelBot.CallHandler.format_data_for_coin_pair(all_exchange_data2)
    #  # print(olol)
    # # print(f'Все данные  : {all_exchange_data2}')
    # # print(f'Все уникальные данные  : {len(all_exchange_data2)}')
    #  for key, value in all_exchange_data2.items():
    #      print(key, value)