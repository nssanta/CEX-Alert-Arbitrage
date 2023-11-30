import logging

from exchange.BaseApi import BaseApi
import okx.MarketData as MarketData

class OkxApi(BaseApi):
    def __init__(self):
        super().__init__()
        self.log_file = 'okx_api.log'
        self.logger = logging.getLogger('OkxApi')


    def get_full_info(self):
        """
        Получаем информацию с помощью API.
        :return: Результат запроса или None в случае ошибки.
        """
        # Устанавливаем флаг для выбора режима торговли
        flag = "0"
        # Создаем экземпляр класса MarketAPI с установленным флагом
        marketDataAPI = MarketData.MarketAPI(flag=flag)
        # Получаем информацию о тикерах с помощью метода get_tickers
        try:
            result = marketDataAPI.get_tickers(instType="SPOT")
            # Возвращаем полученный результат
            return result
        except Exception as e:
            # Логируем ошибку
            self.logger.error(f"Возникла ошибка при получении информации: {e}")
            # Возвращаем None в случае ошибки
            return None
