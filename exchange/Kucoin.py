import json
import time
import hmac
import hashlib
import base64
import httpx
from urllib.parse import quote, urlencode, quote_plus

import requests

from exchange.BaseApi import BaseApi




class Kucoin(BaseApi):
    def __init__(self, name ="Kucoin"):
        # Создаем логгер, используя суперкласс
        super().__init__(log_file="kucoin_api.log",logger="KucoinApi")
        # Имя экземпляра класса
        self.name = name
        # Активирована или нет , для бота в тг
        self.is_selected = True
        # Переменная для ссылки на api (сайт)
        self.domain = "https://api.kucoin.com/"
        # Данные для Авторизации
        self.api_key = 'os.getenv('KUCOIN_API_KEY')'
        self.secret_key = 'os.getenv('KUCOIN_SECRET_KEY')'
        self.pass_api = '@SuperSanta1995'



    async def get_network_commission(self,ccy):
        '''
        Асинхронная функция для получения информации о валюте с API.
        :param ccy: Валюта, для которой нужно получить информацию.
        :return: Словарь с доступными сетями вывода и минимальными и максимальными комиссиями или None в случае ошибки.
        '''
        # Эндпоинт
        endpoint = '/api/v2/deposit-addresses'
        # Данные для запроса
        params = {'currency': ccy}
        # Создаем заголовок
        headers = self._create_header(data=f'?currency={ccy}', endpoint=endpoint)
        # Юрл для запроса
        url = self.domain + endpoint
        print(f'url = {url}')
        # Отправляем запрос
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            print(response)

        if response.status_code == 200:

            return response.json()
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
        pass
    async def get_coins_price_vol(self):
        '''

        :return:
        '''
        pass
    async def get_full_info(self):
        '''

        :return:
        '''
        pass
    async def get_one_coin(self,coin_pair):
        '''

        :param coin_pair:
        :return:
        '''
        pass

    # async def create_deposit_address(self, currency):
    #     method = 'POST'
    #     endpoint = '/api/v1/deposit-addresses'
    #     url = f'https://api.kucoin.com{endpoint}'
    #     data = {"currency": currency}
    #     data_json = json.dumps(data)
    #     headers = self._create_header(method, endpoint, data_json)
    #     response = requests.request(method, url, headers=headers, data=data_json)
    #     return response.status_code, response.json()
    def _create_header(self, endpoint, data=None, method='GET'):
        '''
        Функция для создания заголовка, и подписи
        :param data: Данные передавать в виде данных
        :param endpoint: конечная точка куда будет сделан запрос
        :param method: метод запроса
        :return:
        '''
        # Переводим данные в форма json
        #data_json = json.dumps(data)
        # Иницилизируем время для подписи
        now = int(time.time() * 1000)
        # Создам строку для авторизация
        str_to_sign = str(now) + method + endpoint + data
        print(f'str_to_sign = {str_to_sign}')
        # Создаем сигнатуру
        signature = base64.b64encode(
            hmac.new(self.secret_key.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())#.decode('utf-8')
        # Подписываем
        passphrase = base64.b64encode(
            hmac.new(self.secret_key.encode('utf-8'), self.pass_api.encode('utf-8'), hashlib.sha256).digest())#.decode('utf-8')
        # Формируем заголовок
        # headers = {
        #     "KC-API-SIGN": signature,
        #     "KC-API-TIMESTAMP": str(now),
        #     "KC-API-KEY": self.api_key,
        #     "KC-API-PASSPHRASE": passphrase,
        #     "KC-API-KEY-VERSION": "2",
        #     "Content-Type": "application/json"
        # }
        headers = {
            "KC-API-SIGN": signature,
            "KC-API-TIMESTAMP": str(now),
            "KC-API-KEY": self.api_key,
            "KC-API-PASSPHRASE": passphrase,
            "KC-API-KEY-VERSION": '2'
        }

        return headers



if __name__ == '__main__':
    start_time = time.time()
    async def main():
        kucoin = Kucoin("Kucoin")
        per = await kucoin.get_network_commission('BTC')
        print(per)


    import asyncio
    asyncio.run(main())
    end_time = time.time()
    print(f'Код отработал за {end_time-start_time}')

