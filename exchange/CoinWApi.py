import hashlib
import time

from zope.interface.common import collections

from exchange.BaseApi import BaseApi

import httpx

class CoinWApi(BaseApi):
    def __init__(self, name="CoinW"):
        # Создаем логгер, используя суперкласс
        super().__init__(log_file="coinw_api.log", logger="CoinWApi")
        # Имя класса
        self.name = name
        # Переменная для ссылки на api (сайт)
        self.domain = "https://api.coinw.com"
        # Данные для Авторизации
        self.api_key = "os.getenv('COINW_API_KEY')"
        self.secret_key = "os.getenv('COINW_SECRET_KEY')"
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
                    # Поле стоковое название монеты
                    "coin": list(item.keys())[0],
                    # Поле котировки
                    "price": data["last"],
                    # Поле объем в монетном эквиваленте (первая часть монетной пары)
                    "vol24": data["baseVolume"],
                }
            except Exception as e:
                # Если возникает исключение, логируем ошибку
                self.logger.error(f"Возникла ошибка при обработке информации для пары {pair}: {e}")
        # Возвращаем обработанную информацию
        return processed_info

    async def get_network_commission(self, ccy):
        """
            Создание заголовков запроса для авторизации.
            :return: Заголовки, URL и строка параметров.
        """
        # Формирование конечной точки запроса информации о валюте
        endpoint = self.domain + "/api/v1/public?command=returnCurrencies"
        # Создание заголовков для запроса с авторизацией
        headers = await self._create_headers()
        try:
            # Использование асинхронного клиента для отправки GET-запроса
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, headers=headers)
            response.raise_for_status()
            data = response.json()
            if 'data' in data and ccy in data['data']:
                coin_info = data['data'][ccy]
                return {"сеть*": {"minFee": coin_info["txFee"]}}
            else:
                return None
        except httpx.RequestError as e:
            # Обработка исключения в случае ошибки запроса
            print(f"Request Exception: {e}")
            return None

    async def _create_headers(self, endpoint="", params={}):
        """
            Создание заголовков запроса для авторизации.
            :param endpoint: Конечная точка для запроса.
            :param params: Параметры запроса.
            :return: Заголовки, URL и строка параметров.
        """
        # Формирование упорядоченного словаря параметров для запроса
        sorted_params = collections.OrderedDict(sorted(params.items()))
        # Формирование строки для создания подписи
        signature_string = '&'.join(
            ['{}={}'.format(k, sorted_params[k]) for k in sorted_params]) + f'&secret_key={self.secret_key}'
        # Создание подписи запроса с использованием md5 хэширования
        signature = hashlib.md5(signature_string.encode('utf-8')).hexdigest().upper()
        # Формирование заголовков для запроса
        headers = {
            'api_key': self.api_key,
            'sign': signature,
        }
        return headers

if __name__ == '__main__':
    start_time = time.time()
    async def main():
        okx = CoinWApi("Coin")
        per = await okx.get_network_commission("ETH")
        print(per)
        print()
        print(f'Всего {len(per)}')

    import asyncio

    asyncio.run(main())
    end_time = time.time()
    print(f'Код отработал за {end_time - start_time}')