import time

from exchange.BaseApi import BaseApi
from pybit.unified_trading import HTTP

import httpx

class BybitApi(BaseApi):
    def __init__(self, name ="Okx"):
        # Создаем логгер, используя суперкласс
        super().__init__(log_file="bybit_api.log",logger="BybitApi")
        # Имя класса
        self.name = name

    async def get_full_info(self):
        """
            Асинхронная функция для получения информации с API.
            :return: Результат запроса или None в случае ошибки.
        """
        # URL API, с которого мы будем получать данные
        url = "https://api.bybit.com/v5/market/tickers?category=spot"
        # Список для хранения тикеров
        tickers = []
        # Цикл продолжается, пока есть URL для запроса (ответ не в одной странице)
        async with httpx.AsyncClient() as client:
            while url:
                try:
                    # Выполняем GET-запрос к URL
                    response = await client.get(url)
                    # Проверяем статус ответа
                    if response.status_code == 200:
                        # Если статус ответа 200, преобразуем ответ в JSON
                        data = response.json()
                        # Проверяем код ответа в данных
                        if data["retCode"] == 0:
                            # Если код ответа 0, добавляем список тикеров в наш список
                            tickers.extend(data["result"]["list"])
                            # Проверяем, есть ли URL следующей страницы в данных
                            url = data["result"].get("next_page_url")
                        else:
                            # Если код ответа не 0, выводим сообщение об ошибке и прерываем цикл
                            self.logger.error("Ошибка при получении данных")
                            break
                    else:
                        # Если статус ответа не 200, выводим сообщение об ошибке и прерываем цикл
                        self.logger.error("Ошибка при выполнении запроса")
                        break
                except Exception as e:
                    # Если возникает исключение, логируем ошибку и прерываем цикл
                    self.logger.error(f"Возникла ошибка: {e}")
                    break
        # Возвращаем список тикеров
        return tickers
        # метод библиотеки не асинхроный, пока что морозим его.
        # try:
        #     # Получаем данные с помощью API , с реальной сети и СПОТ
        #     session = HTTP(testnet=False)
        #     ticket = session.get_tickers(category="spot",)
        #     return ticket
        # except Exception as e:
        #     # Логируем ошибку
        #     self.logger.error(f"Возникла ошибка при получении информации: {e}")
        #     # Возвращаем None в случае ошибки
        #     return None
    async def get_coins_price_vol(self):
        """
            Асинхронная функция для обработки данных, полученных от API.
            А именно приводит монетную пару к единому виду и делает словарь, где
            ключ- монетная пара, и значения котировок и объемы в двух валютах.
            :return: Словарь с информацией или None в случае ошибки.
        """
        # Получаем информацию с API
        info = await self.get_full_info()
        # Создаем новый словарь для хранения обработанной информации
        processed_info = {}
        # Обрабатываем каждый элемент в полученной информации
        for item in info:
            try:
                # Получаем монетную пару, преобразуем ее в нижний регистр и удаляем знак "-"
                pair = item["symbol"].lower() #.replace("-", "")
                # Создаем новый словарь для этой пары
                processed_info[pair] = {
                    "price": item["lastPrice"],
                    "volone24": item["volume24h"],
                    #"voltwo24": item[None]
                }
            except Exception as e:
                # Если возникает исключение, логируем ошибку
                self.logger.error(f"Возникла ошибка при обработке информации для пары {pair}: {e}")
        # Возвращаем обработанную информацию
        return processed_info


if __name__ == '__main__':
    start_time = time.time()
    async def main():
        bybit = BybitApi("Bybit")
        per = await bybit.get_coins_price_vol()
        print(per)
        print()
        print(len(per))

    import asyncio
    asyncio.run(main())
    end_time = time.time()
    print(f'Код отработал за {end_time-start_time}')