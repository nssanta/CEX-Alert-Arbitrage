from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes




def keyboard_start_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> ReplyKeyboardMarkup:
    """
        Функция возвращает стартовую клавиатуру после авторизации.
        :param update: Объект Update, содержащий информацию о текущем обновлении.
        :param context: Объект Context, содержащий информацию о текущем контексте.
        :return:
    """
    keyboard = [
        [
            KeyboardButton("Запустить оповещения", ),
            KeyboardButton("Остановить оповещения", ),
        ],
        [KeyboardButton("Настройки")],
        [KeyboardButton("Установить баланс")],
        [KeyboardButton("Запросить котировки", )],
    ]
    # Создаем разметку для клавиатуры
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    return reply_markup
def keyboard_setting_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> ReplyKeyboardMarkup:
    """
        Функция возвращает клавиатуру главного окна настроек.
        :param update: Объект Update, содержащий информацию о текущем обновлении.
        :param context: Объект Context, содержащий информацию о текущем контексте.
        :return:
    """
    keyboard = [
        [KeyboardButton("Таймер")],
        [KeyboardButton("Спред")],
        [KeyboardButton("Объем")],
        [KeyboardButton("Биржи")],
        [KeyboardButton("<- назад")],
    ]
    # Создаем разметку для клавиатуры
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    return reply_markup
def keyboard_setting_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> ReplyKeyboardMarkup:
    """
        Функция возвращает клавиатуру главного окна настроек.
        :param update: Объект Update, содержащий информацию о текущем обновлении.
        :param context: Объект Context, содержащий информацию о текущем контексте.
        :return:
    """
    keyboard = [
        [KeyboardButton("30 секунд")],
        [KeyboardButton("1 минута")],
        [KeyboardButton("2 минуты")],
        [KeyboardButton("5 минут")],
        [KeyboardButton("10 минут")],
        [KeyboardButton("Установить вручную", )],
        [KeyboardButton("<- назад")],
    ]
    # Создаем разметку для клавиатуры
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    return reply_markup

def keyboard_setting_spread(update: Update, context: ContextTypes.DEFAULT_TYPE) -> ReplyKeyboardMarkup:
    """
        Функция возвращает клавиатуру главного окна настроек.
        :param update: Объект Update, содержащий информацию о текущем обновлении.
        :param context: Объект Context, содержащий информацию о текущем контексте.
        :return:
    """
    keyboard = [
        [KeyboardButton("0.8 - 2.5")],
        [KeyboardButton("1 - 2.5")],
        [KeyboardButton("1.5 - 2.5")],
        [KeyboardButton("2 - 2.5")],
        [KeyboardButton("3 - 5")],
        [KeyboardButton("5 - 7")],
        [KeyboardButton("Установить вручную")],
        [KeyboardButton("<- назад")],
    ]
    # Создаем разметку для клавиатуры
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    return reply_markup
def keyboard_setting_exchange(update: Update, context: ContextTypes.DEFAULT_TYPE) -> ReplyKeyboardMarkup:
    """
        Функция возвращает клавиатуру главного окна настроек.
        :param update: Объект Update, содержащий информацию о текущем обновлении.
        :param context: Объект Context, содержащий информацию о текущем контексте.
        :return:
    """
    # Получаем список с контекста
    exchange_list_in_context = context.chat_data.get('EXCHANGE_LIST')
    # Формируем клавиатуру с кнопками бирж из списка в Variable
    #keyboard = [[exchange.name] for exchange in EXCHANGE_LIST]
    keyboard = [[f"✅ {exchange.name}"] if exchange.is_selected else [f"❌ {exchange.name}"] for exchange in exchange_list_in_context]
    keyboard.append(["<- назад"])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    return reply_markup

def keyboard_setting_volume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> ReplyKeyboardMarkup:
    """
        Функция возвращает клавиатуру главного окна настроек.
        :param update: Объект Update, содержащий информацию о текущем обновлении.
        :param context: Объект Context, содержащий информацию о текущем контексте.
        :return:
    """
    keyboard = [
        [KeyboardButton("10000")],
        [KeyboardButton("20000")],
        [KeyboardButton("30000")],
        [KeyboardButton("50000")],
        [KeyboardButton("100000")],
        [KeyboardButton("Установить вручную")],
        [KeyboardButton("<- назад")],
    ]
    # Создаем разметку для клавиатуры
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    return reply_markup