import asyncio
import hashlib
import hmac
import time

import httpx
import requests

from exchange.BaseApi import BaseApi


class GateApi(BaseApi):
    def __init__(self, name = "Gate.io"):
        super().__init__(log_file='gate_api.log', logger='Gate.io')
        # Переменная для имени экземпляра класса
        self.name = name
        # Активирована или нет , для бота в тг
        self.is_selected = False
        # Специфичная переменая для хранения данных сетей и коммисии монет! около 8 тысяч
        self.data_network = None
        # Переменная для ссылки на api (сайт)
        self.domain = "https://api.gateio.ws"
        # Данные для Авторизации
        self.api_key = 'os.getenv('GATE_API_KEY')'
        self.secret_key = 'os.getenv('GATE_SECRET_KEY')'
        self.passphrase = '@SuperSanta1995'

    async def get_full_info(self):
        """
            Асинхронная функция для получения информации с API.
            :return: Результат запроса или None в случае ошибки.
        """
        # Спецефичный метод который создает словарь с сетями и коммисиями, хранит данные в лакальной переменной
        await self._load_network_commission()
        if self.data_network is None:
            self.logger.error("Ошибка при загрузке данных сетей и коммисий self.data_network = None , из get_full_info")
        # Эндпоинт куда отправлять запрос
        endpoint = '/api/v4/spot/tickers'
        url = self.domain+endpoint
        # Заголовок необходим для запроса
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        # Создаем клиент для асинхроного запроса
        async with httpx.AsyncClient() as client:
            try:
                # Выполняем GET-запрос к URL
                response = await client.get(url, headers=headers)
                # Проверяем статус ответа
                if response.status_code == 200:
                    # Если статус ответа 200, преобразуем ответ в JSON
                    data = response.json()
                    return data
                else:
                    # Если статус ответа не 200, выводим сообщение об ошибке и прерываем цикл
                    self.logger.error("Ошибка при выполнении запроса")
                    return {}
            except Exception as e:
                # Если возникает исключение, логируем ошибку и прерываем цикл
                self.logger.error(f"Возникла ошибка: {e}")
    async def get_one_coin(self, coin_pair):
        """
            Асинхронная функция для получения информации о котировках и объеме торгов для указанной монетной пары.
            :param coin_pair: Монетная пара, например, "BTC-USD".
            :return: Словарь с информацией или None в случае ошибки.
        """
        # Эндпоинт куда отправлять запрос
        endpoint = f'/api/v4/spot/tickers?currency_pair={coin_pair}'
        url = self.domain + endpoint
        # Словарь с информацией о котировках и объеме
        processed_info = {}
        # Создаем клиент для асинхронного запроса
        async with httpx.AsyncClient() as client:
            try:
                # Выполняем GET-запрос к URL
                response = await client.get(url)
                # Проверяем статус ответа
                if response.status_code == 200:
                    # Если статус ответа 200, преобразуем ответ в JSON
                    data = response.json()
                    # Преобразуем JSON в словарь
                    pair = coin_pair.lower().replace('_', '')
                    result_vol = round(float(data[0]["base_volume"]), 2)
                    processed_info[pair] = {
                        "coin": coin_pair,
                        "price": data[0]["last"],
                        "vol24": str(result_vol)
                    }
                    return processed_info
                else:
                    self.logger.error(f"Ошибка при выполнении запроса: {response.status_code}")
                    return {}
            except Exception as e:
                self.logger.error(f"Возникла ошибка: {e}")
    async def get_coins_price_vol(self):
        """
            Асинхронная функция для обработки данных, полученных от API.
            А именно приводит монетную пару к единому виду и делает словарь, где
            ключ- монетная пара, и значения котировок и объемы в двух валютах.
            :return: Словарь с информацией или None в случае ошибки.
        """
        try:
            # Словарь с информацией о котировках и объеме
            processed_info = {}
            data = await self.get_full_info()
            for item in data:
                # Преобразуем JSON в словарь
                pair = item["currency_pair"].lower().replace('_', '')
                result_vol = round(float(item["base_volume"]), 2)
                processed_info[pair] = {
                    "coin": item["currency_pair"],
                    "price": item["last"],
                    "vol24": str(result_vol)
                }
            return processed_info

        except Exception as e:
            self.logger.error(f"Возникла ошибка: {e}")
            return {}
        # # Эндпоинт куда отправлять запрос
        # endpoint = f'/api/v4/spot/tickers'
        # url = self.domain + endpoint
        # # Словарь с информацией о котировках и объеме
        # processed_info = {}
        # # Создаем клиент для асинхронного запроса
        # async with httpx.AsyncClient() as client:
        #     try:
        #         # Выполняем GET-запрос к URL
        #         response = await client.get(url)
        #         # Проверяем статус ответа
        #         if response.status_code == 200:
        #             # Если статус ответа 200, преобразуем ответ в JSON
        #             data = response.json()
        #             for item in data:
        #                 # Преобразуем JSON в словарь
        #                 pair = item["currency_pair"].lower().replace('_', '')
        #                 result_vol = round(float(data[0]["base_volume"]), 2)
        #                 processed_info[pair] = {
        #                     "coin": item["currency_pair"],
        #                     "price": data[0]["last"],
        #                     "vol24": str(result_vol)
        #                 }
        #             return processed_info
        #         else:
        #             self.logger.error(f"Ошибка при выполнении запроса: {response.status_code}")
        #             return {}
        #     except Exception as e:
        #         self.logger.error(f"Возникла ошибка: {e}")

    # async def get_network_commission(self, ccy):
    #     """
    #         Асинхронная функция для получения информации о валюте с перемоной Класса.
    #         :param ccy: Валюта, для которой нужно получить информацию.
    #         :return: Словарь с доступными сетями вывода и минимальными и максимальными комиссиями или None в случае ошибки.
    #     """
    #     try:
    #         # Преобразуем данные в словарь для быстрого доступа
    #         data_dict = {item['currency']: item for item in self.data_network}
    #
    #         # Получаем данные для данной валюты
    #         currency_data = data_dict.get(ccy)
    #
    #         if currency_data is None:
    #             self.logger.error(f"Возникла ошибка Монета не найдена: get_network_commission {ccy}")
    #             return {}
    #
    #         # Словарь для хранения данных
    #         commission_data = {}
    #         withdraw_fix_on_chains = currency_data['withdraw_fix_on_chains']
    #         for network, fee_data in withdraw_fix_on_chains.items():
    #             commission_data[network] = {
    #                 'minFee': fee_data,
    #                 'maxFee': fee_data
    #             }
    #         return commission_data
    #
    #     except Exception as e:
    #         self.logger.error(f"Возникла ошибка: {e} get_network_commission {ccy}")
    #         return {}
    # async def get_network_commission(self, ccy):
    #     """
    #         Асинхронная функция для получения информации о валюте с перемоной Класса.
    #         :param ccy: Валюта, для которой нужно получить информацию.
    #         :return: Словарь с доступными сетями вывода и минимальными и максимальными комиссиями или None в случае ошибки.
    #     """
    #     try:
    #         # Преобразуем данные в словарь для быстрого доступа
    #         data_dict = {item['currency']: item for item in self.data_network}
    #
    #         # Получаем данные для данной валюты
    #         currency_data = data_dict.get(ccy)
    #
    #         if currency_data is None:
    #             self.logger.error(f"Возникла ошибка Монета не найдена: get_network_commission {ccy}")
    #             return {}
    #
    #         # Убедимся, что currency_data является словарем
    #         if not isinstance(currency_data, dict):
    #             currency_data = dict(currency_data)
    #
    #         # Словарь для хранения данных
    #         commission_data = {}
    #         withdraw_fix_on_chains = currency_data.get('withdraw_fix_on_chains')
    #
    #         # Убедимся, что withdraw_fix_on_chains является словарем
    #         if not isinstance(withdraw_fix_on_chains, dict):
    #             withdraw_fix_on_chains = dict(withdraw_fix_on_chains)
    #
    #         for network, fee_data in withdraw_fix_on_chains.items():
    #             commission_data[network] = {
    #                 'minFee': fee_data,
    #                 'maxFee': fee_data
    #             }
    #         return commission_data
    #
    #     except Exception as e:
    #         self.logger.error(f"Возникла ошибка: {e} get_network_commission {ccy}")
    #         return {}

    async def get_network_commission(self, ccy):
        """
            Асинхронная функция для получения информации о валюте с перемоной Класса.
            :param ccy: Валюта, для которой нужно получить информацию.
            :return: Словарь с доступными сетями вывода и минимальными и максимальными комиссиями или None в случае ошибки.
        """
        #self._load_network_commission(self)
        try:
            # Словарь для хранения данных
            commission_data = {}
            for currency_data in self.data_network:
                if currency_data['currency'] == ccy:
                    withdraw_fix_on_chains = currency_data['withdraw_fix_on_chains']
                    for network, fee_data in withdraw_fix_on_chains.items():
                        commission_data[network] = {
                            'minFee': fee_data,
                            'maxFee': fee_data
                        }
            return commission_data

        except Exception as e:
            self.logger.error(f"Возникла ошибка Монета не найдена: {e} get_network_commission {ccy}")
            return {}
        # Запускаем цикл по данным
        # for coin_data in self.data_network:
        #     # Если это наша монета
        #     if coin_data["currency"] == ccy:
        #         coin_info = coin_data
        #         # Формируем словарь с названием сети и коммисией
        #         for network, comission in coin_info['withdraw_fix_on_chains'].items():
        #             network_name = network  # f"{network['name']}"
        #             min_fee = comission
        #             max_fee = comission
        #             commission_data[network_name] = {
        #                 'minFee': min_fee,
        #                 'maxFee': max_fee
        #             }

    async def _load_network_commission(self):
        """
            Специфичный метод который делает запрос на все сети и коммисию сразу и сохроняет данные в переменную класса.
            :return: Словарь с доступными сетями вывода и минимальными и максимальными комиссиями или None в случае ошибки.
        """
        # try:
        #     # Адрес для запроса информации
        #     url=self.domain+"/api/v4/wallet/withdraw_status"
        #     # Заголовок необходим для заполнения запроса
        #     headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        #     # Создаем подписаный заголовок
        #     sign_headers = self._create_headers()
        #     headers.update(sign_headers)
        #     async with httpx.AsyncClient() as client:
        #         # Выполняем GET-запрос к URL
        #         response = await client.get(url, headers=headers)
        #         # print(f'response = {response.json()}')
        #         # self.logger.error(f'RESPONSE = \n {response.status_code}')
        #         #  преобразуем ответ в JSON
        #         self.data_network = response.json()
        # except Exception as e:
        #     self.logger.error(f"Возникла ошибка при создание словаря с монетами : {e}")
        #     # Если вызвало ошибку ждем две секунды и пробуем снова.
        #     await asyncio.sleep(2)
        #     await self._load_network_commission()
        try:
            # Данные для запроса
            #endpoint = '/api/v3/capital/config/getall'
            # Заголовок необходим для заполнения запроса
            headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
            # Создаем подписаный заголовок
            sign_headers = self._create_headers()
            url = self.domain+"/api/v4/wallet/withdraw_status"
            # Делаем запрос
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=sign_headers)
                # Сохраняем данные в переменую класса.
                self.data_network = response.json()
                # print(f'DATA = {response.json()}')
        except Exception as e:
            self.logger.error(f"Возникла ошибка: {e} _load_network_commission")
            await asyncio.sleep(2)
            await self._load_network_commission()

    def _create_headers(self, method='GET', url='/api/v4/wallet/withdraw_status', query_string="", payload_string=""):
        '''
            Создает подписаный заголовок
            :param method:
            :param url:
            :param query_string:
            :param payload_string:
            :return:
        '''
        timestamp = str(int(time.time()))
        sha512_payload = hashlib.sha512(payload_string.encode(
            'utf-8')).hexdigest() if payload_string \
            else "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e"

        signature_string = f"{method}\n{url}\n{query_string}\n{sha512_payload}\n{timestamp}"
        signature = hmac.new(self.secret_key.encode('utf-8'), signature_string.encode('utf-8'), hashlib.sha512).hexdigest()

        return {'KEY': self.api_key, 'Timestamp': timestamp, 'SIGN': signature}




if __name__ == "__main__":
    async def main():
        ga = GateApi("Gate.io")
       # await ga._load_network_commission()
        full = await ga.get_coins_price_vol()
        print(full)
        print(len(full))



    asyncio.run(main())
    # host = "https://api.gateio.ws"
    # prefix = "/api/v4"
    # headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    #
    # url = '/spot/currency_pairs'
    # query_param = ''
    # r = requests.request('GET', host + prefix + url, headers=headers)
    # print(r.json())
    # print()
    # print(len(r.json()))