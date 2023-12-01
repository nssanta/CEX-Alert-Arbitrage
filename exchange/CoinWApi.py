import time

from exchange.BaseApi import BaseApi

import httpx

class CoinWApi(BaseApi):
    def __init__(self, name="CoinW"):
        # Создаем логгер, используя суперкласс
        super().__init__(log_file="coinw_api.log", logger="CoinWApi")
        # Имя класса
        self.name = name

    async def get_full_info(self):
        """
            Асинхронная функция для получения информации с API.
            :return: Результат запроса или None в случае ошибки.
        """
        # URL API, с которого мы будем получать данные
        url = "https://api.coinw.com/api/v1/public?command=returnTicker"
        # Список для хранения тикеров
        tickers = []
        async with httpx.AsyncClient() as client:
            try:
                # Выполняем GET-запрос к URL
                response = await client.get(url)
                # Проверяем статус ответа
                if response.status_code == 200:
                    # Если статус ответа 200, преобразуем ответ в JSON
                    data = response.json()
                    # Проверяем код ответа в данных
                    if data["code"] == "200":
                        # Итерируемся по ключам и значениям в data["data"]
                        for pair_name, pair_data in data["data"].items():
                            # Создаем словарь, содержащий название монетной пары и ее данные
                            ticker_info = {pair_name: pair_data}
                            # Добавляем словарь в список tickers
                            tickers.append(ticker_info)
                        # # Если код ответа 0, добавляем список тикеров в наш список
                        # tickers.extend(data["data"].values())
                    else:
                        # Если код ответа не 0, выводим сообщение об ошибке и прерываем цикл
                        self.logger.error("Ошибка при получении данных")
                else:
                    # Если статус ответа не 200, выводим сообщение об ошибке и прерываем цикл
                    self.logger.error("Ошибка при выполнении запроса")
            except Exception as e:
                # Если возникает исключение, логируем ошибку и прерываем цикл
                self.logger.error(f"Возникла ошибка: {e}")
        return tickers


if __name__ == '__main__':
    start_time = time.time()
    async def main():
        okx = CoinWApi("Coin")
        per = await okx.get_full_info()
        print(per)

    import asyncio

    asyncio.run(main())
    end_time = time.time()
    print(f'Код отработал за {end_time - start_time}')