import json
import time
import hmac
import hashlib
import base64
import httpx
from urllib.parse import quote, urlencode, quote_plus

import requests

from exchange.BaseApi import BaseApi




class KucoinApi(BaseApi):
    def __init__(self, name ="Kucoin"):
        # Создаем логгер, используя суперкласс
        super().__init__(log_file="kucoin_api.log", logger="KucoinApi")
        # Имя экземпляра класса
        self.name = name
        # Активирована или нет , для бота в тг
        self.is_selected = True
        # Специфичная переменая для хранения данных сетей и коммисии монет! около 8 тысяч
        self.data_network = None
        # Переменная для ссылки на api (сайт)
        self.domain = "https://api.kucoin.com"
        # Данные для Авторизации
        self.api_key = os.getenv('KUCOIN_API_KEY')
        self.secret_key = os.getenv('KUCOIN_SECRET_KEY')
        self.pass_api = '@SuperSanta1995'
    async def get_full_info(self):
        """
            Асинхронная функция для получения информации с API.
            :return: Результат запроса или None в случае ошибки.
        """
        # Загружаем/Обновляем данные о сетях
        await self._load_network_commission()

        # Эндпоинт для запроса "Get all tickers"
        endpoint = "/api/v1/market/allTickers"
        url = self.domain + endpoint

        try:
            async with httpx.AsyncClient() as client:
                # Выполняем GET-запрос к эндпоинту
                response = await client.get(url)

                # Проверяем статус ответа
                if response.status_code == 200:
                    # Если статус ответа 200, парсим JSON ответа
                    data = response.json()

                    return data['data']["ticker"]

                else:
                    # Если статус ответа не 200, логируем ошибку HTTP
                    self.logger.error("Ошибка HTTP запроса. Код статуса: {} get_full_info".format(response.status_code) )

        except Exception as e:
            # Логируем любые исключения, возникшие во время запроса
            self.logger.error("Во время запроса произошла ошибка: {} get_full_info".format(e))

        # Возвращаем None в случае ошибки
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
                pair = item["symbol"].lower().replace("-", "")
                # Округляем число объема
                result = round(float(item['volValue']),2)
                # Создаем новый словарь для этой пары
                processed_info[pair] = {
                    # Поле стоковое название монеты
                    "coin": item["symbol"],
                    # Поле котировки
                    "price": item["last"],
                    # Поле объем в монетном эквиваленте (первая часть монетной пары)\
                    "vol24": str(result)#item["volume24h"],
                }
            except Exception as e:
                # Если возникает исключение, логируем ошибку
                self.logger.error(f"Возникла ошибка при обработке информации для пары {pair}: {e}")
        # Возвращаем обработанную информацию
        return processed_info
    async def get_one_coin(self, coin_pair):
        """
        Асинхронная функция для получения данных первого уровня рынка для указанной монетной пары.
        :param символ: Монетная пара, например, "BTC-USDT"
        :return: Словарь с информацией о котировке для указанной монетной пары или None в случае ошибки.
        """
        # Эндпоинт для запроса данных первого уровня рынка
        endpoint = "/api/v1/market/orderbook/level1"
        url = self.domain + endpoint

        try:
            info = await self.get_full_info()
            # Итерируем по данным
            for item in info:
                if item['symbol'] == coin_pair: # ищем нашу монетную пару
                    # Формат ключа
                    pair = coin_pair.lower().replace('-', '')
                    processed_info = {
                        pair: {
                            "coin": item['symbol'],
                            "price": item["last"],
                            "vol24": item['volValue']
                        }
                    }
                    return processed_info

        except Exception as e:
            # Логируем другие неожиданные исключения
            self.logger.error(f"Во время запроса произошла неожиданная ошибка: {e} get_one_coin")

        # Возвращаем None в случае ошибки
        return None
    async def get_order_book(self, ccy, limit=20):
        '''
        Функция для получения книги ордеров для монетной пары (стандартно для 20 стаканов)
        :param self:
        :param symbol: монетная пара (например, "BTC-USDT")
        :param limit: количество элементов в книге ордеров
        :return: данные книги ордеров
        '''
        base_url = self.domain + f"/api/v1/market/orderbook/level2_{limit}"
        params = {"symbol": ccy}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(base_url, params=params)
                data = response.json()
                return data['data']
        except Exception as e:
            print(f"Возникла ошибка: {e} в функции get_order_book")

    async def _load_network_commission(self):
        """
            Специфичный метод который делает запрос на все сети и коммисию сразу и сохроняет данные в переменную класса.
            :param ccy: Валюта, для которой нужно получить информацию.
            :return: Словарь с доступными сетями вывода и минимальными и максимальными комиссиями или None в случае ошибки.
        """
        try:
            # Данные для запроса
            endpoint = '/api/v3/currencies'
            #headers, query_string = self._create_headers(endpoint)
            url = self.domain + endpoint
            # Делаем запрос
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                data = response.json()
                # Сохраняем данные в переменую класса.
                self.data_network = data['data']
        except Exception as e:
            self.logger.error(f"Возникла ошибка: {e} __get_network_commission")

    async def get_network_commission(self, ccy):
        """
        Асинхронная функция для получения информации о валюте с API.
        :param ccy: Валюта, для которой нужно получить информацию.
        :return: Словарь с доступными сетями вывода и минимальными и максимальными комиссиями или None в случае ошибки.
        """
        try:
            # Словарь для хранения данных
            commission_data = {}
            # Запускаем цикл по данным
            for coin_data in self.data_network:
                # Если это наша монета
                if coin_data['currency'] == ccy:
                    # собираем данные
                    for network in coin_data['chains']:
                        network_name = network['chainName']  # Название сети
                        min_fee = network['withdrawalMinSize']  # Минимальная колличество вывода
                        max_fee = '-'  # Максимальная колличество вывода
                        commission = network['withdrawalMinFee']  # Комиссия вывода
                        # Множитель( Кратность вывода)
                        # factor = network['withdrawIntegerMultiple']
                        contract = network['contractAddress']  # Адресс контракта , если он имеется.
                        # Работает ли сеть для вывода
                        enabled = 'Да' if str(network.get('isWithdrawEnabled', False)).capitalize() == 'True' else 'Нет'
                        # Работает ли сеть для ввода
                        in_enabled = 'Да' if str(network.get('isDepositEnabled', False)).capitalize() == 'True' else 'Нет'

                        commission_data[network_name] = {
                            'enabled': enabled,
                            'in_enabled': in_enabled,
                            'minFee': commission,
                            'maxFee': commission,
                            'outMin': min_fee,
                            'outMax': max_fee,
                            'contract': contract[-6:],
                            # 'factor': factor,
                            # 'oneaddr': oneaddr

                        }
                    return commission_data


        except Exception as e:
            self.logger.error(f"Возникла ошибка Монета не найдена: {e} get_network_commission")
            return {}
    # async def create_deposit_address(self, currency):
    #     method = 'POST'
    #     endpoint = '/api/v1/deposit-addresses'
    #     url = f'https://api.kucoin.com{endpoint}'
    #     data = {"currency": currency}
    #     data_json = json.dumps(data)
    #     headers = self._create_header(method, endpoint, data_json)
    #     response = requests.request(method, url, headers=headers, data=data_json)
    #     return response.status_code, response.json()
    # def _create_header(self, endpoint, params=None, method='GET'):
    #     '''
    #     Функция для создания заголовка, и подписи
    #     :param data: Данные передавать в виде данных
    #     :param endpoint: конечная точка куда будет сделан запрос
    #     :param method: метод запроса
    #     :return:
    #     '''
    #     now = int(time.time() * 1000)
    #     str_to_sign = str(now) + method + endpoint
    #
    #     if params:
    #         str_to_sign += '?' + '&'.join([f'{key}={value}' for key, value in params.items()])
    #
    #     signature = base64.b64encode(
    #         hmac.new(self.secret_key.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest()
    #     )
    #     passphrase_signature = base64.b64encode(
    #         hmac.new(self.secret_key.encode('utf-8'), self.pass_api.encode('utf-8'), hashlib.sha256).digest()
    #     )
    #
    #     headers = {
    #         "KC-API-SIGN": signature,
    #         "KC-API-TIMESTAMP": str(now),
    #         "KC-API-KEY": self.api_key,
    #         "KC-API-PASSPHRASE": passphrase_signature,
    #         "KC-API-KEY-VERSION": '2'
    #     }
    #
    #     return headers
    #
    # async def get_network_commission(self, ccy):
    #     '''
    #     Асинхронная функция для получения информации о валюте с API.
    #     :param ccy: Валюта, для которой нужно получить информацию.
    #     :return: Словарь с доступными сетями вывода и минимальными и максимальными комиссиями или None в случае ошибки.
    #     '''
    #     # Эндпоинт
    #     endpoint = '/api/v2/deposit-addresses'
    #     # Данные для запроса
    #     params = {"currency": ccy}
    #     # Создаем url адресс
    #     url = self.domain + endpoint
    #     # Создаем заголовок
    #     print(url)
    #     headers = self._create_header(params=params, endpoint=endpoint)
    #     # Отправляем запрос
    #     with httpx.Client() as client:
    #         response = client.get(url, params=params, headers=headers)
    #         print(response)
    #         return response
    #
    #     # # Эндпоинт
    #     # endpoint = '/api/v2/deposit-addresses'
    #     # # Данные для запроса
    #     # params = {'currency': ccy}
    #     # # Создаем заголовок
    #     # headers = self._create_header(data=f'?currency={ccy}', endpoint=endpoint)
    #     # # Юрл для запроса
    #     # url = self.domain + endpoint
    #     # print(f'url = {url}')
    #     # # Отправляем запрос
    #     # async with httpx.AsyncClient() as client:
    #     #     response = await client.get(url, headers=headers)
    #     #     print(response)
    #     #
    #     # if response.status_code == 200:
    #     #
    #     #     return response.json()
    #     # else:
    #     #     print(f"Error {response.status_code}: {response.text}")
    #     #     return None
    #     # pass

if __name__ == '__main__':
    start_time = time.time()
    async def main():
        kucoin = KucoinApi("Kucoin")
        await kucoin.get_full_info()
        await kucoin._load_network_commission()
        per = await kucoin.get_network_commission('GMEE')
        print(per)
        print(len(per))


    import asyncio
    asyncio.run(main())
    end_time = time.time()
    print(f'Код отработал за {end_time-start_time}')

