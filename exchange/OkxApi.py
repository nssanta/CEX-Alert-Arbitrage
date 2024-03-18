import base64
import hashlib
import hmac
import json
import time
from datetime import datetime, timezone

import httpx
import logging

import numpy as np
from exchange.BaseApi import BaseApi


class OkxApi(BaseApi):
    def __init__(self, name ="Okx"):
        # Создаем логгер, используя суперкласс
        super().__init__(log_file='okx_api.log',logger='OkxApi')
        # Переменная для имени экземпляра класса
        self.name = name
        # Активирована или нет , для бота в тг
        self.is_selected = True
        # Переменная для ссылки на api (сайт)
        self.domain = "https://www.okx.com"
        # Данные для Авторизации
        self.api_key = 'os.getenv('OKX_API_KEY')'
        self.secret_key = 'os.getenv('OKX_SECRET_KEY')'
        self.passphrase = '@Seva1995'

    async def get_one_coin(self, coin_pair):
        """
            Асинхронная функция для получения информации о котировках и объеме торгов для указанной монетной пары.
            :param coin_pair: Монетная пара, например, "BTC-USD".
            :return: Словарь с информацией или None в случае ошибки.
        """
        # Формируем конечную точку и URL для запроса
        endpoint = f"/api/v5/market/ticker?instId={coin_pair}"
        url = self.domain + endpoint
        try:
            async with httpx.AsyncClient() as client:
                # Отправляем GET-запрос к API
                response = await client.get(url)
                if response.status_code == 200:
                    # Получаем данные в формате JSON
                    data = response.json()
                    if data["code"] == "0":
                        processed_info = {}
                        # Обработка данных для каждого элемента в полученной информации
                        for item in data["data"]:
                            try:
                                # Получаем монетную пару, преобразуем ее в нижний регистр и удаляем знак "-"
                                pair = item["instId"].lower().replace("-", "")
                                resultvol = round(float(item['volCcy24h']), 2)
                                # Создаем словарь с информацией о котировках и объеме торгов для этой пары
                                processed_info[pair] = {
                                    "coin": item["instId"],
                                    "price": item["last"],
                                    "vol24": str(resultvol),
                                }
                            except Exception as e:
                                self.logger.error(f"Ошибка обработки элемента: {e}")
                        return processed_info
                    else:
                        self.logger.error(f"Ошибка: {data['msg']}")
                else:
                    self.logger.error(f"Запрос завершился с кодом ошибки: {response.status_code}")
        except Exception as e:
            self.logger.error(f"Ошибка запроса: {e}")
        return None
    async def get_full_info(self):
        """
            Асинхронная функция для получения информации с API.
            :return: Результат запроса или None в случае ошибки.
        """
        # URL API, с которого мы будем получать данные
        endpoint = "/api/v5/market/tickers?instType=SPOT"
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
                    self.logger.error(f"Возникла ошибка: {e} в get_full_info")
                    break
        # Возвращаем список тикеров
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
                # Получаем монетную пару, преобразуем ее в нижний регистр и удаляем знак "-"
                pair = item["instId"].lower().replace("-", "")
                # Округляем число объема
                #result = round(float(item["vol24h"]) * float(item["last"]), 2)
                resultvol = round(float(item['volCcy24h']),2)
                # Создаем новый словарь для этой пары
                processed_info[pair] = {
                    # Поле стоковое название монеты
                    "coin": item["instId"],
                    # Поле котировки
                    "price": item["last"],
                    # Поле объем в монетном эквиваленте (первая часть монетной пары)
                    "vol24": str(resultvol),
                }
            except Exception as e:
                self.logger.error(f"Возникла ошибка: {e} в get_coins_price_vol ")
        # Возвращаем обработанную информацию
        return processed_info
    async def get_network_commission(self,ccy):
        """
            Асинхронная функция для получения информации о валюте с API.
            :param ccy: Валюта, для которой нужно получить информацию.
            :return: Словарь с доступными сетями вывода и минимальными и максимальными комиссиями или None в случае ошибки.
        """
        # Эндпоинт спецеально для создания заголовка.
        endpoint = f"/api/v5/asset/currencies?ccy={ccy}"
        # Создаем сам заголовок.
        headers = self._create_headers(endpoint=endpoint)
        # URL API, с которого мы будем получать данные
        url = self.domain+endpoint
        # Словарь для хранения информации о валюте
        currency_info = {}
        try:
            # Получаем остальные данные с другого эндпоинта.
            contract_data = await self.get_contract_address(ccy)
            async with httpx.AsyncClient() as client:
                # Выполняем GET-запрос к URL
                response = await client.get(url, headers= headers)
                # Проверяем статус ответа
                if response.status_code == 200:
                    # Если статус ответа 200, преобразуем ответ в JSON
                    data = response.json()
                    # Проверяем код ответа в данных
                    if data["code"] == "0":
                        # Если код ответа 0, добавляем информацию о валюте в наш словарь
                        for item in data["data"]:
                            if item["ccy"] == ccy:
                                enabled = 'Да' if str(item.get('canWd', False)).capitalize() == 'True' else 'Нет'
                                in_enabled = 'Да' if str(item.get('canDep', False)).capitalize() == 'True' else 'Нет'
                                # Цикл по данным контракта для получения тех которые соответствуют сети.
                                for contr in contract_data:
                                    if contr['chain'] == item["chain"]:
                                        contract = contr["ctAddr"]
                                    else:
                                        contract = None
                                currency_info[item["chain"]] = {
                                    'enabled': enabled,
                                    'in_enabled': in_enabled,
                                    "minFee": item["minFee"],
                                    "maxFee": item["maxFee"],
                                    'outMin': item["minWd"],
                                    'outMax': item["maxWd"],
                                    'contract': contract,#[-6:],
                                    # "minFeeForCtAddr": item["minFeeForCtAddr"],
                                    # "maxFeeForCtAddr": item["maxFeeForCtAddr"]
                                }
                    else:
                        # Если код ответа не 0, выводим сообщение об ошибке
                        self.logger.error("Ошибка при получении данных")
        except Exception as e:
            # Если возникает исключение, логируем ошибку
            self.logger.error(f"Возникла ошибка: {e}")
        # Возвращаем информацию о валюте
        return currency_info

    async def get_contract_address(self, coin):
        """
            Метод который принимает монету и возвращает адресс контракта.
            :return: адресс контракта.
        """
        # Эндпоинт спецеально для создания заголовка.
        endpoint = f"/api/v5/asset/deposit-address?ccy={coin}"
        # Создаем сам заголовок.
        headers = self._create_headers(endpoint=endpoint)
        url = self.domain + endpoint
        try:
            # Делаем запрос
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                data = response.json()
                # Если ответ не пустой возвращаем значение адресса контракта
                return data['data']
                # return data[0]['contract_address'] if data else None
        except Exception as e:
            self.logger.error(f"Возникла ошибка: {e} get_contract_address {coin}")
            return None
    def _create_headers(self, request_type="GET", endpoint="", body=""):
        """
            Специфический метод, который создает берет данные аккаунта, (API) и создает заголовок для запроса
            :param request_type: Тип запроса
            :param endpoint: Адресс запроса
            :param body: Тело сообщения
            :return: ответ от сервера
        """
        # Генерация временной метки
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        # Преобразуем тело заголовка в json , если оно есть.
        if body != '':
            body = json.dumps(body)
        # Формирование строки для подписи
        message = timestamp + request_type.upper() + endpoint + body
        # Создаем подпись
        mac = hmac.new(bytes(self.secret_key, 'utf-8'), bytes(message, 'utf-8'), digestmod='sha256')
        # Кодируем подпись в base64
        signature = base64.b64encode(mac.digest())
        # Формируем заголовок запроса
        headers = {
            'CONTENT-TYPE': 'application/json',
            'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self.passphrase
        }
        # Возврат сформированных заголовков
        return headers

    async def get_order_book(self, pair, book_depth=20):
        '''
        Функция для запроса стаканов
        :param instrument_id:
        :param order_book_depth:
        :return:
        '''
        # Определите URL конечной точки
        endpoint = f"/api/v5/market/books?instId={pair}&sz={book_depth}"

        # Составьте URL запроса с параметрами
        url = self.domain + endpoint

        # Настройте заголовки запроса при необходимости
        headers = {
            "Content-Type": "application/json",
            # Добавьте другие заголовки по мере необходимости
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                data = response.json()
                return data['data'][0]
        except Exception as e:
            self.logger.error(f"Возникла ошибка: {e} функция get_order_book")


if __name__ == '__main__':
    start_time = time.time()
    async def main():
        okx = OkxApi("Okx")

        #per = await okx.get_full_info()
        #print(per)
        # order = await okx.get_order_book('BTC-USDC')
        # print(order)
        lol = await okx.get_network_commission('TAMA')
        print(lol)

       # print(len(per))


    import asyncio

    asyncio.run(main())
    end_time = time.time()
    print(f'Код отработал за {end_time - start_time}')

# STX-USDT XRP-BTC TON-USDT