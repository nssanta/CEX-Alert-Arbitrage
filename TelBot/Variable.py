import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from Core.DataHandler import DataHandler

# Список кому доступен бот
WhiteList = [
    '6219851487',
    '6348339423',
    '1271372091',
]
# Пароль
PASSWORD = "A"

# Состояния диалога
PASS_STATE = 0                  # Авторизация
AUTH_STATE = 1                  # Ввод пароля
WORKING_STATE = 2               # Обычное состояния, где работает главное меню
SETTING_STATE = 3               # Работа в контексте меню Настройки
TIMER_SETTING_STATE = 4         # Состояние выбора времени таймера оповещения
SPREAD_SETTING_STATE = 5        # Состояние выбора min-max спреда
INPUT_TIME_SETTING_STATE = 6    # Состояние ручного ввода интервала для таймера
INPUT_SPRED_SETTING_STATE = 7    # Состояние ручного ввода интервала для таймера

async def initialize_variables(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
        Функция, которыя запускается после авторизации и инициализирует переменные для работы,
        в контексте сохраняются переменные в работе бота и переменные связаные с конкретным диалогом
        :param update: Объект Update, содержащий информацию о текущем обновлении.
        :param context: Объект Context, содержащий информацию о текущем контексте.
        :return:
    """
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

