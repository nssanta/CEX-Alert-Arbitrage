import base64
import hashlib
import hmac
import json
import time

import httpx
import requests

from exchange.BaseApi import BaseApi


class MexcApi(BaseApi):
    def __init__(self, name ="Mexc"):
        # Создаем логгер, используя суперкласс
        super().__init__(log_file='mexc_api.log',logger='Mexc')
        # Переменная для имени экземпляра класса
        self.name = name
        # Активирована или нет , для бота в тг
        self.is_selected = True
        # Специфичная переменая для хранения данных сетей и коммисии монет! около 8 тысяч
        self.data_network = None
        # Переменная для ссылки на api (сайт)
        #self.domain = "https://api.mexc.com"
        self.domain = "https://www.mexc.com"
        # Данные для Авторизации
        self.api_key = 'mx0vglwHDo6E88yURw'
        self.secret_key = '41c1149ceec443b981d195452712812a'
        self.passphrase = '@SuperSanta1995'
    async def get_full_info(self):
        """
            Асинхронная функция для получения информации с API.
            :return: Результат запроса или None в случае ошибки.
        """
        # !!!!!!
        # Запускаем метод для получения сетей и коммиссии для всех доступных моент. Специфичный метод и подход.
        await self._get_network_commission()

        # URL API, с которого мы будем получать данные
        #endpoint = "/api/v3/exchangeInfo?permissions=SPOT"
        endpoint ='/open/api/v2/market/ticker'
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
                        if data["code"] == 200:
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
    async def get_one_coin(self, coin_pair):
        """
            Асинхронная функция для получения информации о котировках для указанной монетной пары.
            :param symbol: Монетная пара, например, BTC_CNYT.
            :return: Словарь с информацией о котировках или None в случае ошибки.
        """
        # Формируем URL для запроса к API
        endpoint = f"/open/api/v2/market/ticker?symbol={coin_pair}"
        url = f"{self.domain}{endpoint}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    # Проверяем наличие ключа 'data' и его непустое значение
                    if 'data' in data and data['data'] is not None:
                        data_info = data['data'][0]
                        processed_info = {}
                        try:
                            pair = coin_pair.lower().replace('_', '')
                            result_vol = round(float(data_info["volume"]), 2)
                            processed_info[pair] = {
                                "coin": coin_pair,
                                "price": data_info["last"],
                                "vol24": str(result_vol)
                            }
                            return processed_info
                        except Exception as e:
                            # Логируем ошибку обработки информации
                            self.logger.error(f"Ошибка при обработке информации для пары {coin_pair}: {e}")
                            return {}
                    else:
                        # Логируем отсутствие данных о котировках
                        self.logger.error(f"Отсутствуют данные о котировках для {coin_pair}")
                        return {}
                else:
                    # Логируем ошибку при запросе
                    self.logger.error(f"Ошибка при запросе: {response.status_code}")
                    return {}
        except Exception as e:
            # Логируем общую ошибку
            self.logger.error(f"Ошибка: {e}")
            return {}
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
                pair = item["symbol"].lower().replace("_", "")
                # Округляем число объема
                # result = round(float(item["vol24h"]) * float(item["last"]), 2)
                resultvol = round(float(item['volume']), 2)
                # Создаем новый словарь для этой пары
                processed_info[pair] = {
                    # Поле стоковое название монеты
                    "coin": item["symbol"],
                    # Поле котировки
                    "price": item["last"],
                    # Поле объем в монетном эквиваленте (первая часть монетной пары)
                    "vol24": str(resultvol),
                }
            except Exception as e:
                self.logger.error(f"Возникла ошибка: {e}")
        # Возвращаем обработанную информацию
        return processed_info
    async def get_network_commission(self, ccy):
        """
            Асинхронная функция для получения информации о валюте с перемоной Класса.
            :param ccy: Валюта, для которой нужно получить информацию.
            :return: Словарь с доступными сетями вывода и минимальными и максимальными комиссиями или None в случае ошибки.
        """
        try:
            # Словарь для хранения данных
            commission_data = {}
            # Запускаем цикл по данным
            for coin_data in self.data_network:
                # Если это наша монета
                if coin_data["coin"] == ccy:
                    coin_info = coin_data
                    # Формируем словарь с названием сети и коммисией
                    for network in coin_info['networkList']:
                        network_name = network['network']# f"{network['name']}"
                        min_fee = network['withdrawMin']
                        max_fee = network['withdrawMax']

                        commission_data[network_name] = {
                            'minFee': min_fee,
                            'maxFee': max_fee
                        }
            return commission_data
        except Exception as e:
            self.logger.error(f"Возникла ошибка Монета не найдена: {e} get_network_commission")
            return {}
    async def _get_network_commission(self):
        """
            Специфичный метод который делает запрос на все сети и коммисию сразу и сохроняет данные в переменную класса.
            :param ccy: Валюта, для которой нужно получить информацию.
            :return: Словарь с доступными сетями вывода и минимальными и максимальными комиссиями или None в случае ошибки.
        """
        try:
            # Данные для запроса
            endpoint = '/api/v3/capital/config/getall'
            headers, query_string = self._create_headers(endpoint)
            url = f'https://api.mexc.com{query_string}'
            # Делаем запрос
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                # Сохраняем данные в переменую класса.
                self.data_network = response.json()
        except Exception as e:
            self.logger.error(f"Возникла ошибка: {e} __get_network_commission")
    def _create_headers(self, request_type="GET", endpoint="/api/v3/capital/config/getall", body=""):
        """
            Специфический метод, который создает берет данные аккаунта, (API) и создает заголовок для запроса
            :return: ответ от сервера
        """
        try:
            timestamp = str(int(time.time() * 1000))
            recv_window = '5000'
            total_params = f'timestamp={timestamp}&recvWindow={recv_window}'
            # Create the signature for the endpoint
            signature = hmac.new(self.secret_key.encode('utf-8'), total_params.encode('utf-8'), hashlib.sha256).hexdigest()
            headers = {
                'X-MEXC-APIKEY': self.api_key,
            }
            query_string = f'{endpoint}?{total_params}&signature={signature}'

            return headers, query_string
        except Exception as e:
            self.logger.error(f"Возникла ошибка: {e} __create_headers")
            return [], ""

if __name__ == '__main__':
    start_time = time.time()
    async def main():
        mexc = MexcApi("Mexc")
        per = await mexc.get_full_info()
        print(per)
        print()
        print(len(per))


    import asyncio

    asyncio.run(main())
    end_time = time.time()
    print(f'Код отработал за {end_time - start_time}')