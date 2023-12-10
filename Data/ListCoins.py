import httpx
import logging
import asyncio

class ListCoins:
    def __init__(self, log_file = 'listcoins.log', logger = "ListCoins", name = "ListCoins"):
        self.log_file = log_file
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.ERROR)

        # Создаем файл, если он не существует
        open(self.log_file, 'a').close()

        # Проверяем, не добавлен ли уже файловый хендлер
        if not self.logger.handlers:
            file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
            file_handler.setLevel(logging.ERROR)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

            # Добавляем обработчик потока, который выводит сообщения в консоль
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.ERROR)
            stream_handler.setFormatter(formatter)
            self.logger.addHandler(stream_handler)

            # Имя класса
            self.name = name
            # Переменная для хранения списка
            self.coins = set()
            # # Переменая при иницилизации запускает функцию
            self.data = {}
            #asyncio.run(self._initialize_data())
    def disable_stream_handler(self):
        '''
            Метод выключает логинг в консоль
        '''
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                self.logger.removeHandler(handler)

    async def initialize_data(self):
        """
        Асинхронная функция для инициализации данных.
        """
        try:
            # Пытаемся получить и объединить данные
            self.data = await self._merge_data()
        except Exception as e:
            # В случае ошибки логируем исключение
            self.logger.error(f"Ошибка при инициализации данных: {e}")
    async def get_coinw_data(self):
        """
        Асинхронная функция для получения информации о монетах с API Coinw.
        :return: Словарь с данными о монетах или пустой словарь в случае ошибки.
        """
        url = "https://api.coinw.com/api/v1/public?command=returnTicker"

        # Словарь для хранения данных о монетах
        coins_dict = {}

        async with httpx.AsyncClient() as client:
            try:
                # Выполняем GET-запрос к URL
                response = await client.get(url)

                # Проверяем статус ответа
                if response.status_code == 200:
                    # Преобразуем ответ в JSON
                    data = response.json()

                    # Проверяем код ответа в данных
                    if data["code"] == "200":
                        # Обрабатываем данные о парамах монет
                        for pair_name, pair_data in data["data"].items():
                            coin1, coin2 = pair_name.split('_')
                            coins_dict[coin1 + coin2] = {
                                "coin1": coin1,
                                "coin2": coin2
                            }
                    else:
                        # Если код ответа не 200, логируем ошибку
                        self.logger.error("Ошибка при получении данных")
                else:
                    # Если статус ответа не 200, логируем ошибку
                    self.logger.error("Ошибка при выполнении запроса")

            except Exception as e:
                # Логируем возникшее исключение
                self.logger.error(f"Возникла ошибка в get_coinw_data: {e}")

        # Возвращаем словарь с данными о монетах
        return coins_dict
    async def get_okx_data(self):
        """
            Асинхронная функция для получения информации с API.
            :return: Результат запроса или None в случае ошибки.
        """
        # URL API, с которого мы будем получать данные
        url = "https://www.okx.com/api/v5/market/tickers?instType=SPOT"
        # Список для хранения тикеров
        tickers = []
        # Цикл продолжается, пока есть URL для запроса (ответ не в одной странице)
        async with httpx.AsyncClient() as client:
            while url:
                try:
                    # Словарь для хранения монет
                    coins_dict = {}
                    # Выполняем GET-запрос к URL
                    response = await client.get(url)
                    # Проверяем статус ответа
                    if response.status_code == 200:
                        # Если статус ответа 200, преобразуем ответ в JSON
                        data = response.json()
                        # Проверяем код ответа в данных
                        if data["code"] == "0":
                            ticker_data = data.get("data", [])  # Получаем данные из словаря data
                            for item in ticker_data:
                                coin1, coin2 = item["instId"].split("-")
                                coins_dict[coin1 + coin2] = {
                                    "coin1": coin1,
                                    "coin2": coin2
                                }
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
        # Возвращаем словарь с монетами
        return coins_dict
    async def _merge_data(self):
        """
        Асинхронная функция для объединения данных из разных источников.
        """
        try:
            # Вызываем асинхронные методы для получения данных
            coinw_data, okx_data = await asyncio.gather(self.get_coinw_data(), self.get_okx_data())

            # Объединяем данные в один общий словарь, учитывая только уникальные ключи
            combined_data = {}
            combined_data.update(coinw_data)
            for k, v in okx_data.items():
                if k not in combined_data:
                    combined_data[k] = v

            # Обработка объединенных данных, если нужно

            return combined_data
        except Exception as e:
            # Логируем ошибку при объединении данных
            self.logger.error(f"Возникла ошибка при объединении данных: {e}")
            return None
    async def get_first_coin(self, pair):
        """
        Асинхронная функция для получения первой монеты из пары.
        :param pair: Пара монет в формате "coin1coin2".
        :return: Название первой монеты из пары или сообщение об ошибке.
        """
        # Приводим входную строку к нижнему регистру
        lower_pair = pair.lower()
        try:
            for key in self.data:
                # Сравниваем ключи в нижнем регистре
                if key.lower() == lower_pair:
                    return self.data[key]["coin1"]
        except Exception as e:
            # Если монета не найдена, логируем ошибку
            self.logger.error(f"Монета не найдена для пары {pair} ощиюка - {e} - функция get_first_coin")

        return "Монета не найдена"


if __name__ == "__main__":

    # Пример использования
    your_class = ListCoins()
    # okx = asyncio.run(your_class.get_okx_data())
    # coinw = asyncio.run(your_class.get_coinw_data())
    #
    # merg = asyncio.run(your_class.merge_data())
    # print(merg)
    # print("\n")
    # print(len(okx))
    # print(len(coinw))
    # print(len(merg))
    aga = asyncio.run(your_class.get_first_coin("BTCUSDC"))
    print(f'aga {aga}')
