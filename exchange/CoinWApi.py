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
                # Получаем монетную пару, преобразуем ее в нижний регистр и удаляем знак "_"
                pair = list(item.keys())[0].lower().replace("_", "")
                data = list(item.values())[0]
                # Создаем новый словарь для этой пары
                processed_info[pair] = {
                    "price": data["last"],
                    "volone24": data["baseVolume"],
                }
            except Exception as e:
                # Если возникает исключение, логируем ошибку
                self.logger.error(f"Возникла ошибка при обработке информации для пары {pair}: {e}")
        # Возвращаем обработанную информацию
        return processed_info


if __name__ == '__main__':
    start_time = time.time()
    async def main():
        okx = CoinWApi("Coin")
        per = await okx.get_coins_price_vol()
        print(per)
        print()
        print(f'Всего монет {len(per)}')

    import asyncio

    asyncio.run(main())
    end_time = time.time()
    print(f'Код отработал за {end_time - start_time}')