import asyncio

from exchange.BybitApi import BybitApi
from exchange.CoinWApi import CoinWApi
from exchange.OkxApi import OkxApi
from collections import Counter

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

# if __name__ == "__main__":
#     # Создаем экземпляры API
#     okx = OkxApi("Okx")
#     bybit = BybitApi("Bybit")
#     coinw = CoinWApi("CoinW")
#
#     # Создаем экземпляр DataHandler
#     data_handler = DataHandler()
#
#     # Запускаем
#     common_pairs = asyncio.run(data_handler.get_common_pairs([okx, bybit, coinw]))
#     print(common_pairs)
#     print(len(common_pairs))


