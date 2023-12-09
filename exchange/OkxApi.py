import base64
import hashlib
import hmac
import json
import time
from datetime import datetime, timezone

import httpx
import logging

from exchange.BaseApi import BaseApi
import okx.MarketData as MarketData
import okx.Account as Account

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
        self.api_key = 'be0263b3-e366-4df4-91aa-01ac1e431b5a'
        self.secret_key = '752444EDE261ADF4EA58E24C3B553644'
        self.passphrase = '@SuperSanta1995'

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
                    self.logger.error(f"Возникла ошибка: {e}")
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
                self.logger.error(f"Возникла ошибка: {e}")
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
        async with httpx.AsyncClient() as client:
            try:
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
                                currency_info[item["chain"]] = {
                                    "minFee": item["minFee"],
                                    "maxFee": item["maxFee"],
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

    async def get_firt_coin(self, instId, tdMod="isolated", ccy=None, px=None, leverage=None, unSpotOffset=None):
        """
        Асинхронная функция для получения максимального объема покупки и продажи для заданной монетной пары.
        :param instId: Монетная пара (например, BTC-USDT).
        :param tdMode: Режим торговли (cross, isolated, cash).
        :param ccy: Валюта используемая для маржи (при необходимости).
        :param px: Цена (необязательно, будет рассчитана по последней торговой цене).
        :param leverage: Плечо (при необходимости).
        :param unSpotOffset: Флаг для отключения/включения смещения риска между спотом и деривативами (при необходимости).
        :return: Словарь с максимальным объемом покупки и продажи для указанной монетной пары.
        """
        # Формируем параметры запроса
        params = {
            'instId': instId,
            #'tdMode': tdMode
        }
        if ccy:
            params['ccy'] = ccy
        if px:
            params['px'] = px
        if leverage:
            params['leverage'] = leverage
        if unSpotOffset is not None:
            params['unSpotOffset'] = unSpotOffset

        # Формируем URL API
        url = self.domain+'/api/v5/account/max-size'

        # Выполняем запрос к API
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    if data["code"] == "0" and data["data"]:
                        return {
                            "maxBuy": data["data"][0]["maxBuy"],
                            "maxSell": data["data"][0]["maxSell"]
                        }
                    else:
                        return {"error": "Ошибка при получении данных"}
            except Exception as e:
                return {"error": f"Ошибка запроса: {e}"}
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




if __name__ == '__main__':
    start_time = time.time()
    async def main():
        okx = OkxApi("Okx")
        per = await okx.get_full_info()
        print(per)
        print()
       # print(len(per))


    import asyncio

    asyncio.run(main())
    end_time = time.time()
    print(f'Код отработал за {end_time - start_time}')

# STX-USDT XRP-BTC TON-USDT