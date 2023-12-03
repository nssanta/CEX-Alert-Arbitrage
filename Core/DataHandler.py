import asyncio
import time

from exchange.BybitApi import BybitApi
from exchange.CoinWApi import CoinWApi
from exchange.OkxApi import OkxApi
from collections import Counter

import numpy as np

class DataHandler:
    def __init__(self, name = "DataHandler"):
        self.name = name

    async def get_common_pairs(self, apis):
        # Создаем список задач для каждого API, чтобы получить данные асинхронно
        tasks = [api.get_coins_price_vol() for api in apis]
        # Запускаем все задачи асинхронно и ждем их завершения
        results = await asyncio.gather(*tasks)
        # Получаем список всех пар из всех словарей
        all_pairs = [pair for result in results for pair in result.keys()]
        # Считаем количество каждой пары
        pair_counts = Counter(all_pairs)
        # Находим общие пары, которые есть в каждом словаре
        # Это те пары, количество которых равно количеству API
        common_pairs = [pair for pair, count in pair_counts.items() if count == len(apis)]

        return common_pairs

if __name__ == "__main__":
    start_time = time.time()
    async def main():
        okx = OkxApi("Okx")
        bybit = BybitApi("Bybit")
        coinw = CoinWApi("Coin W")
        DH =DataHandler("DH")

        per = await DH.get_common_pairs([okx, bybit, coinw])
        print(per)
        print()
        print(f'Всего {len(per)}')
    asyncio.run(main())
    end_time = time.time()
    print(f'Код отработал за {end_time - start_time}')

# Сделать метод который примет список с монетами,
# потом он берет список со словарями, и берет их по парно и запускает в новом потоке скрипт который выявит разницу между
# котировками и вернут данные, и так пока не завершатся все потоки. А потом компануем данные для передачи их анализатору.



