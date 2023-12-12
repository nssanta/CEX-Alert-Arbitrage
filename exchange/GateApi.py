import asyncio

import httpx
import requests

from exchange.BaseApi import BaseApi


class GateApi(BaseApi):
    def __init__(self, name = "Gate.io"):
        super().__init__(log_file='gate_api.log', logger='Gate.io')
        # Переменная для имени экземпляра класса
        self.name = name
        # Активирована или нет , для бота в тг
        self.is_selected = True
        # Специфичная переменая для хранения данных сетей и коммисии монет! около 8 тысяч
        self.data_network = None
        # Переменная для ссылки на api (сайт)
        self.domain = "https://api.gateio.ws"
        # Данные для Авторизации
        # self.api_key = 'mx0vglwHDo6E88yURw'
        # self.secret_key = '41c1149ceec443b981d195452712812a'
        # self.passphrase = '@SuperSanta1995'
    async def get_full_info(self):
        """
            Асинхронная функция для получения информации с API.
            :return: Результат запроса или None в случае ошибки.
        """
        # Эндпоинт куда отправлять запрос
        endpoint = '/api/v4/spot/currency_pairs'
        url = self.domain+endpoint
        # Заголовок необходим для запроса
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        # Цикл продолжается, пока есть URL для запроса (ответ не в одной странице)
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

    async def get_one_coin(self,coin_pair):
        pass
    async def get_network_commission(self,ccy):
        pass
    async def get_coins_price_vol(self):
        pass






if __name__ == "__main__":
    async def main():
        ga = GateApi("Gate.io")
        full = await ga.get_full_info()
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