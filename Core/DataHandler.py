import asyncio
import time
from itertools import permutations

from exchange.BybitApi import BybitApi
from exchange.CoinWApi import CoinWApi
from exchange.OkxApi import OkxApi
from collections import Counter

import numpy as np

class DataHandler:
    def __init__(self, name = "DataHandler"):
        self.name = name

    # async def get_common_pairs(self, apis):
    #     # Создаем список задач для каждого API, чтобы получить данные асинхронно
    #     tasks = [api.get_coins_price_vol() for api in apis]
    #     # Запускаем все задачи асинхронно и ждем их завершения
    #     results = await asyncio.gather(*tasks)
    #     # Получаем список всех пар из всех словарей
    #     all_pairs = [pair for result in results for pair in result.keys()]
    #     # Считаем количество каждой пары
    #     pair_counts = Counter(all_pairs)
    #     # Находим общие пары, которые есть в каждом словаре
    #     # Это те пары, количество которых равно количеству API
    #     common_pairs = [pair for pair, count in pair_counts.items() if count == len(apis)]
    #
    #     return common_pairs
    async def get_common_pairs_and_data(self, apis):
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
                if 0.7 < dif <= 20:
                    result[pair] = {
                        'data': {
                            api1.name: data1[pair],
                            api2.name: data2[pair]
                        },
                        'dif': dif
                    }

        return result

    async def get_all_exchange_data(self, apis):
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

        #   # Получаем общие пары и данные от всех API
        #   common_pairs, all_data = await DH.get_common_pairs_and_data(ex_list)
        # #  print(f'Общие пары: {common_pairs}')
        #   print(f'Всего общих пар: {len(common_pairs)}')

        # Получаем все данные обмена
        all_exchange_data = await DH.get_all_exchange_data(ex_list)
        print(f'Все данные  : {all_exchange_data}')
        print(f'Все уникальные данные  : {len(all_exchange_data)}')


    asyncio.run(main())

    end_time = time.time()
    print(f'Код отработал за {end_time - start_time}')

# Сделать метод который примет список с монетами,
# потом он берет список со словарями, и берет их по парно и запускает в новом потоке скрипт который выявит разницу между
# котировками и вернут данные, и так пока не завершатся все потоки. А потом компануем данные для передачи их анализатору.



