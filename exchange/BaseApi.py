
import logging
from abc import ABC, abstractmethod

class BaseApi(ABC):
    def __init__(self, log_file = 'base_api.log', logger = "BaseApi", name = "Base"):
        # Имя класса
        self.name = name
        # Активирована или нет , для бота в тг
        self.is_selected = True

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

    def disable_stream_handler(self):
        '''
            Метод выключает логинг в консоль
        '''
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                self.logger.removeHandler(handler)
    @abstractmethod
    async def get_full_info(self):
        """
            Метод для получения данных с Api
            :return: ответ сервера
        """
        pass
    @abstractmethod
    async def get_coins_price_vol(self):
        """
            Метод для обработки данных от сервера, для последующих операций.
            :return:
        """
    @abstractmethod
    async def get_network_commission(self,ccy):
        """
            Метод для получения коммиссии и сети вывода.
        :return:
        """

