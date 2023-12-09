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
        [KeyboardButton("Биржи")],
        [KeyboardButton("Монеты")],
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
        [KeyboardButton("Установить вручную (в секундах)", )],
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
        [KeyboardButton("0.5 - 2.5")],
        [KeyboardButton("0.6 - 2.5")],
        [KeyboardButton("0.7 - 2.5")],
        [KeyboardButton("0.8 - 2.5")],
        [KeyboardButton("0.9 - 2.5")],
        [KeyboardButton("1 - 2.5")],
        [KeyboardButton("Установить вручную(min-max)")],
        [KeyboardButton("<- назад")],
    ]
    # Создаем разметку для клавиатуры
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    return reply_markup