import asyncio
import os

import logging
from telegram import Update
from telegram.ext import ContextTypes

from Core.DataHandler import DataHandler
from exchange.BybitApi import BybitApi
from exchange.CoinWApi import CoinWApi
from exchange.GateApi import GateApi
from exchange.MexcApi import MexcApi
from exchange.OkxApi import OkxApi

#   ЛОГИРОВАНИЕ В ФАЙЛ И КОНСОЛЬ!
log_file = "variable.log"
logger = logging.getLogger("Variable")
logger.setLevel(logging.ERROR)
# Создаем файл, если он не существует
open(log_file, 'a').close()
# Проверяем, не добавлен ли уже файловый хендлер
if not logger.handlers:
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    # Добавляем обработчик потока, который выводит сообщения в консоль
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.ERROR)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
def disable_stream_handler(self):
    '''
        Метод выключает логинг в консоль
    '''
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            logger.removeHandler(handler)

# Список кому доступен бот
WhiteList = [
    '6219851487',
    '6348339423',
    '1271372091',
]
# Пароль
PASSWORD = "A"
#PASSWORD = os.getenv('bot_pass')

# Состояния диалога
PASS_STATE = 0                      # Авторизация
AUTH_STATE = 1                      # Ввод пароля
WORKING_STATE = 2                   # Обычное состояния, где работает главное меню
SETTING_STATE = 3                   # Работа в контексте меню Настройки
TIMER_SETTING_STATE = 4             # Состояние выбора времени таймера оповещения
SPREAD_SETTING_STATE = 5            # Состояние выбора min-max спреда
INPUT_TIME_SETTING_STATE = 6        # Состояние ручного ввода интервала для таймера
INPUT_SPRED_SETTING_STATE = 7       # Состояние ручного ввода интервала для таймера
EXCHANGE_SETTING_STATE = 8          # Состояние выбора бирж для фильтра
INPUT_COINPAIR_SETTING_STATE = 9    # Состояние ввода пользователем монетной пары


async def initialize_variables(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
        Функция, которыя запускается после авторизации и инициализирует переменные для работы,
        в контексте сохраняются переменные в работе бота и переменные связаные с конкретным диалогом
        :param update: Объект Update, содержащий информацию о текущем обновлении.
        :param context: Объект Context, содержащий информацию о текущем контексте.
        :return:
    """
    try:
        # Перменная которая будет проверять вызывалась ли текущая функция иницилизации переменых
        context.chat_data.setdefault('INITIALIZED', True)
        # Иницилизируем переменную для хранения авторизованых юзеров в контексте бота
        context.bot_data.setdefault('AUTHORIZED_USERS', [])
        # Иницилизируем переменную для хранения "задачи" цикла оповещания - который явл. task asyncl
        context.chat_data['ALERT_TASK'] = None
        # Переменная иницилизирует DataHandler для каждого юзера отдельный экземпляр.
        context.chat_data.setdefault('DH_Class', DataHandler("DH"))
        # Инициализируем данные монет в контроллере
        asyncio.ensure_future(context.chat_data.get('DH_Class').ListCoins.initialize_data())
        # Переменнай иницилизирует таймер отправки уведомлений
        context.chat_data.setdefault('TIMER_ALERT', 60)
        # Переменная которая будет хранить список бирж
        context.chat_data.setdefault('Okx', OkxApi("Okx"))
        context.chat_data.setdefault('Bybit', BybitApi("Bybit"))
        context.chat_data.setdefault('Coin W', CoinWApi("Coin W"))
        context.chat_data.setdefault('Mexc', MexcApi("Mexc"))
        context.chat_data.setdefault('Gate.io', GateApi("Gate.io"))

        context.chat_data.setdefault('EXCHANGE_LIST', [
            context.chat_data.get('Okx'),
            context.chat_data.get('Bybit'),
            context.chat_data.get('Coin W'),
            context.chat_data.get('Mexc'),
            context.chat_data.get('Gate.io'),

        ])
    except Exception as e:
        logger.error(f"Возникла ошибка: {e} функция initialize_variables")


