import time

import httpx
import logging

from exchange.BaseApi import BaseApi
import okx.MarketData as MarketData

class OkxApi(BaseApi):
    def __init__(self, name ="Okx"):
        # Создаем логгер, используя суперкласс
        super().__init__(log_file='okx_api.log',logger='OkxApi')
        self.name = name
    # def get_full_info1(self):
    #     """
    #     Получаем информацию с помощью API.
    #     :return: Результат запроса или None в случае ошибки.
    #     """
    #     # Устанавливаем флаг для выбора режима торговли
    #     flag = "0"
    #     # Создаем экземпляр класса MarketAPI с установленным флагом
    #     marketDataAPI = MarketData.MarketAPI(flag=flag)
    #     # Получаем информацию о тикерах с помощью метода get_tickers
    #     try:
    #         result = marketDataAPI.get_tickers(instType="SPOT")
    #         # Возвращаем полученный результат
    #         return result
    #     except Exception as e:
    #         # Логируем ошибку
    #         self.logger.error(f"Возникла ошибка при получении информации: {e}")
    #         # Возвращаем None в случае ошибки
    #         return None
    async def get_full_info(self):
        """
            Асинхронная функция для получения информации с API.
            :return: Результат запроса или None в случае ошибки.
        """
        # URL API, с которого мы будем получать данные
        url = "https://www.okx.com/api/v5/market/tickers?instType=SPOT"
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
                        if data["code"] == "0":
                            # Если код ответа 0, добавляем список тикеров в наш список
                            tickers.extend(data["data"])
                            # Проверяем, есть ли URL следующей страницы в данных
                            url = None  # В данном API нет пагинации, поэтому мы устанавливаем url в None
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


if __name__ == '__main__':
    start_time = time.time()
    async def main():
        okx = OkxApi("Okx")
        per = await okx.get_full_info()
        print(per)

    import asyncio

    asyncio.run(main())
    end_time = time.time()
    print(f'Код отработал за {end_time - start_time}')