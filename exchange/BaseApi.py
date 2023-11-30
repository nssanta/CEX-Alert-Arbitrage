import logging
from abc import ABC, abstractmethod

class BaseApi(ABC):
    def __init__(self):
        self.log_file = 'base_api.log'
        self.logger = logging.getLogger('BaseApi')
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
            for handler in self.logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    self.logger.removeHandler(handler)
    @abstractmethod
    def get_full_info(self):
        '''
            Метод для получения данных с Api
            :return: ответ сервера
        '''
        pass

