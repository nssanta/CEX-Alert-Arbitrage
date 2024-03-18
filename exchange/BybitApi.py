import hashlib
import hmac
import inspect
import time
from urllib.parse import quote, urlencode, quote_plus

from exchange.BaseApi import BaseApi
from pybit.unified_trading import HTTP

import httpx

class BybitApi(BaseApi):
    def __init__(self, name ="Bybit"):
        # Создаем логгер, используя суперкласс
        super().__init__(log_file="bybit_api.log",logger="BybitApi")
        # Имя экземпляра класса
        self.name = name
        # Активирована или нет , для бота в тг
        self.is_selected = True
        # Переменная для ссылки на api (сайт)
        self.domain = "https://api.bybit.com"
        # Данные для Авторизации
        self.api_key = 'os.getenv('BYBIT_API_KEY')'
        self.secret_key = 'os.getenv('BYBIT_SECRET_KEY')'
    async def get_full_info(self):
        """
            Асинхронная функция для получения информации с API.
            :return: Результат запроса или None в случае ошибки.
        """
        # URL API, с которого мы будем получать данные
        endpoint = "/v5/market/tickers?category=spot"
        url = self.domain+endpoint
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

    async def get_one_coin(self, coin_pair):
        """
            Асинхронная функция для обработки данных, полученных от API для одной монетной пары.
            :param coin_pair: Монетная пара, например, "BTCUSDT"
            :return: Словарь с информацией о котировке и объеме для указанной монетной пары или None в случае ошибки.
        """
        try:
            # Получаем информацию с API
            info = await self.get_full_info()
            # Ищем информацию для указанной монетной пары
            for item in info:
                pair = item["symbol"].lower()
                if pair == coin_pair.lower():
                    # Найдена информация для указанной монетной пары
                    result = round(float(item["volume24h"]) * float(item["lastPrice"]), 2)
                    processed_info = {
                        pair: {
                            "coin": item["symbol"],
                            "price": item["lastPrice"],
                            "vol24": str(result)
                        }
                    }
                    return processed_info
            # Если информация для указанной монетной пары не найдена
            self.logger.error(f"Информация для монетной пары {coin_pair} не найдена.")
            return None
        except Exception as e:
            # Если возникает исключение, логируем ошибку
            self.logger.error(f"Возникла ошибка при обработке информации для пары {coin_pair}: {e}")
            return None
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
                # Округляем число объема
                result = round(float(item["volume24h"]) * float(item["lastPrice"]),2)
                # Создаем новый словарь для этой пары
                processed_info[pair] = {
                    # Поле стоковое название монеты
                    "coin": item["symbol"],
                    # Поле котировки
                    "price": item["lastPrice"],
                    # Поле объем в монетном эквиваленте (первая часть монетной пары)\
                    "vol24": str(result)#item["volume24h"],
                }
            except Exception as e:
                # Если возникает исключение, логируем ошибку
                self.logger.error(f"Возникла ошибка при обработке информации для пары {pair}: {e}")
        # Возвращаем обработанную информацию
        return processed_info
    async def get_network_commission(self, ccy):
        """
        Асинхронная функция для получения информации о валюте с API.
        :param ccy: Валюта, для которой нужно получить информацию.
        :return: Словарь с доступными сетями вывода и минимальными и максимальными комиссиями или None в случае ошибки.
        """
        # Эндпоинт для запроса информации о валюте
        endpoint = f"/asset/v3/private/coin-info/query"
        # Создание заголовков запроса
        headers, url, full_param_str = await self._create_headers2(endpoint)
        # Использование асинхронного клиента для отправки запроса
        async with httpx.AsyncClient() as client:
            # Выполнение GET-запроса к API
            response = await client.get(f"{url}?{full_param_str}", headers=headers)
            if response.status_code == 200:
                # Если ответ успешный (статус 200), обработка данных
                data = response.json()
                currency_info = {}
                if 'result' in data:
                    # Парсинг информации о валюте из ответа API
                    for item in data['result']['rows']:
                        if item.get('coin') == ccy:
                            for chain in item.get('chains', []):
                                currency_info[chain["chain"]] = {
                                    "minFee": chain["withdrawFee"],
                                    "maxFee": chain["withdrawFee"]
                                }
                return currency_info
            else:
                # Обработка других статусов ответа (не 200)
                return None
    async def _create_headers2(self, endpoint) -> dict:
        """
            Создание заголовков запроса для авторизации.
            :param endpoint: Конечная точка для запроса.
            :return: Заголовки, URL и строка параметров.
        """
        # Формирование словаря параметров для запроса
        params = {
            "api_key": self.api_key,
            "timestamp": round(time.time() * 1000),
            "recv_window": 5000
        }
        # Преобразование параметров в строку для формирования подписи
        param_str = urlencode(sorted(params.items(), key=lambda tup: tup[0]))
        # Создание подписи запроса
        hash = hmac.new(bytes(self.secret_key, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
        # Получение подписи в виде строки из хэша
        signature = hash.hexdigest()
        # Создание словаря с подписью
        sign_real = {"sign": signature}
        # Кодирование параметров с добавленной подписью в URL-совместимую строку
        param_str = quote_plus(param_str, safe="=&")
        # Формирование строки параметров с добавленной подписью для включения в запрос
        full_param_str = f"{param_str}&sign={sign_real['sign']}"
        # Формирование URL для запроса
        url = self.domain + endpoint
        # Формирование заголовков запроса
        headers = {"Content-Type": "application/json"}
        return headers, url, full_param_str

    async def _create_headers(self, endpoint) -> dict:
        params = {
            "api_key": self.api_key,
            "timestamp": round(time.time() * 1000),
            "recv_window": 5000
        }

        # Соблюдение порядка параметров
        param_str = urlencode(sorted(params.items(), key=lambda tup: tup[0]))

        # Использование корректного кодирования
        param_str = quote(param_str, safe="=&")

        # Формирование строки для подписи
        sign_str = f"{endpoint.split('/')[-1]}{param_str}"

        # Создание подписи запроса
        hash = hmac.new(bytes(self.secret_key, "utf-8"), sign_str.encode("utf-8"), hashlib.sha256)
        signature = hash.hexdigest()

        # Формирование заголовков запроса
        headers = {
            "Content-Type": "application/json",
            "sign": signature,
            "X-BAPI-API-KEY": self.api_key,
            "timestamp": str(params["timestamp"]),
            "recv-window": str(params["recv_window"])
        }

        return headers, self.domain + endpoint

    async def get_order_book(self, symbol, limit=20):
        '''
        Функция для получения книги ордеров для монетной пары
        :param symbol: монетная пара
        :param limit: лимит для размера данных
        :return: данные книги ордеров
        '''

        endpoint = '/spot/v3/public/quote/depth'
        url = self.domain + endpoint
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        params = {'symbol': symbol, 'limit': limit}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params)
                data = response.json()
                return data['result']
        except Exception as e:
            self.logger.error(f"Возникла ошибка: {e} в функции get_order_book")



if __name__ == '__main__':
    start_time = time.time()
    async def main():
        bybit = BybitApi("Bybit")
        per = await bybit.get_one_coin('BTCUSDT')
        # per = await bybit.get_full_info()
        print(per)
        # print()
        # print(len(per))
        #
        # ceti = await bybit.get_network_commission('USDT')
        # print(ceti)
        #
        # ppp = await bybit.get_order_book('BTCUSDT')
        # print(ppp['bids'])

    import asyncio
    asyncio.run(main())
    end_time = time.time()
    print(f'Код отработал за {end_time-start_time}')