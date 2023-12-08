#!/usr/bin/env python3

import os

import logging
import asyncio

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, \
    ForceReply, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import filters, Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, CallbackContext

from Core.DataHandler import DataHandler
from TelBot import UiBot, UiHandler
from exchange.BybitApi import BybitApi
from exchange.CoinWApi import CoinWApi
from exchange.OkxApi import OkxApi

#______________________________________________________________________________________________________________________
# СПИСОК КОНСТАНТ
# Токен бота
#TOKEN = os.getenv('bot_token')#environ.get("bot_token")
TOKEN = "os.getenv('TELEGRAM_BOT_TOKEN')"
# Список кому доступен бот
WhiteList = [
    '6219851487',
    '6348339423',
    '1271372091',
]
# Пароль
#PASSWORD = os.getenv('bot_pass')#environ.get("bot_pass")
#PASSWORD = "AmadisLoveMoneyAndCrypt"
PASSWORD = "A"
# Список для авторизованых пользователей
AUTHORIZED_USERS = []
# Переменная для управления циклом
ALERT_TASK = None

#______________________________________________________________________________________________________________________
# ИНИЦИЛИЗИРУЕМ КОНТРОЛЕР АПИ.
okx = OkxApi("Okx")
bybit = BybitApi("Bybit")
coinw = CoinWApi("Coin W")

ex_list = []
ex_list.append(okx)
ex_list.append(bybit)
ex_list.append(coinw)

DH = DataHandler("DH")
#______________________________________________________________________________________________________________________

# Вывод логирования в терминал
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# выводим get и post
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """
#         Стартовая функция, которая проверяет белый список на доступ к боту, а также запрашивает пароль
#         :param update:
#         :param context:
#         :return:
#     """
#     user_id = update.effective_user.id
#     authorized_users = context.bot_data.setdefault('AUTHORIZED_USERS', [])
#
#     if str(user_id) not in authorized_users:
#     # user = update.effective_user.id
#     # logger.info(f"user = {user}")
#     #if not str(user_id) in AUTHORIZED_USERS:
#         if str(user_id) in WhiteList:
#             await update.message.reply_text('Пожалуйста, введите пароль', reply_markup=ForceReply())
#         else:
#             await update.message.reply_text('Извините, вы не в белом списке')
#     else:
#         await update.message.reply_text('Вы уже авторизованы')
async def passauth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
        Стартовая функция, которая проверяет белый список на доступ к боту, а также запрашивает пароль
        :param update: Объект Update, содержащий информацию о текущем обновлении.
        :param context: Объект Context, содержащий информацию о текущем контексте.
        :return:
    """
    # Получаем ID пользователя
    user_id = update.effective_user.id
    # Получаем список авторизованных пользователей
    authorized_users = context.bot_data.setdefault('AUTHORIZED_USERS', [])
    # Проверяем, авторизован ли пользователь
    if str(user_id) not in authorized_users:
        # Если пользователь в белом списке, запрашиваем пароль
        if str(user_id) in WhiteList:
            await update.message.reply_text('Пожалуйста, введите пароль', reply_markup=ReplyKeyboardRemove())
        else:
            # Если пользователь не в белом списке, отправляем сообщение об ошибке
            await update.message.reply_text('Извините, вас нет в списке', reply_markup=ReplyKeyboardRemove())
    else:
        # Если пользователь уже авторизован, отправляем сообщение об этом
        await update.message.reply_text('Вы уже авторизованы')
async def password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
        Функция которая вызывается для авторизованых пользователей, проверяет пароль и
        при авторизации добавляет id пользователя в AUTHORIZED_USERS, список который будет проверятся дальше.
        :param update: Объект Update, содержащий информацию о текущем обновлении.
        :param context: Объект Context, содержащий информацию о текущем контексте.
        :return:
    """
    # Получаем ID пользователя
    user = update.effective_user.id
    # Проверяем ответ пользователя, правильно ли он ввел пароль
    if update.message.text == PASSWORD:
        # Добавляем ID пользователя в сессию бота
        context.bot_data.setdefault('AUTHORIZED_USERS', []).append(str(user))
        # Выводим сообщение об удачной аутентификации
        await update.message.reply_text('Доступ разрешен\nДальнейшее управление через интерактивное меню',
                                        reply_markup=UiBot.keyboard_start_menu(update, context))
    else:
        # Выводим сообщение об не удачной аутентификации
        await update.message.reply_text('Неверный пароль')

async def alerts_loop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
        Функция которая делает уведомления у нее бесконечный цикл
        :param update: Объект Update, содержащий информацию о текущем обновлении.
        :param context: Объект Context, содержащий информацию о текущем контексте.
        :return:
    """
    while True:
        try:
            # Запрашиваем данные с API
            data_api = await DH.get_best_ticker(ex_list)
            # Форматируем данные для отправки
            messages = await format_data(data_api)
            # Отправляем каждое сообщение с задержкой 2 секунды
            if messages:
                await update.effective_chat.send_message("🚀")
            for msg in messages:
                await update.effective_chat.send_message(msg)
                await asyncio.sleep(2)
            # Пауза в секундах для всего блока уведомлений
            await asyncio.sleep(90)
        except Exception as e:
            # Обработка ошибок (можно записать лог, отправить уведомление и т.д.)
            # Можно вывести информацию об ошибке
            logger.error(f"Произошла ошибка: {e}")
            # Продолжаем цикл, не прерывая выполнение программы
            continue
async def start_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
        Функция включает уведомления
        :param update: Объект Update, содержащий информацию о текущем обновлении.
        :param context: Объект Context, содержащий информацию о текущем контексте.
        :return:
    """
    # Проверяем, запущены ли уже оповещения
    if 'ALERT_TASK' in context.chat_data and context.chat_data['ALERT_TASK'] is not None:
        await update.effective_chat.send_message('Оповещения уже запущены')
        return
    # Сообщаем пользователю
    await update.message.reply_text("Вы включили оповещения!")
    # Запускаем цикл оповещений
    context.chat_data['ALERT_TASK'] = asyncio.create_task(alerts_loop(update, context))
async def stop_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
        Функция выключает уведомления
        :param update: Объект Update, содержащий информацию о текущем обновлении.
        :param context: Объект Context, содержащий информацию о текущем контексте.
        :return:
    """
    # Проверяем, остановлены ли уже оповещения
    if 'ALERT_TASK' not in context.chat_data or context.chat_data['ALERT_TASK'] is None:
        await update.effective_chat.send_message('Оповещения уже остановлены')
        return
    # Сообщаем пользователю
    await update.effective_chat.send_message("Оповещения отключены!")
    # Останавливаем цикл оповещений
    context.chat_data['ALERT_TASK'].cancel()
    context.chat_data['ALERT_TASK'] = None
async def request_quotes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_chat.send_message('Функция в разработке, не спешите.')
    pass
async def format_data(data):
    """
    Функция для форматирования данных, полученных от API, в сообщения для отправки.
    :param data: Данные, полученные от API.
    :return: Список сообщений для отправки.
    """
    messages = []
    for exchange, coins in data.items():
        for coin, coin_data in coins.items():
            # Получаем названия бирж из блока 'data'
            exchange_names = list(coin_data['data'].keys())
            # Формируем строку с названиями бирж
            exchange_string = ' ➤ '.join(exchange_names)
            # Начинаем формирование сообщения для каждой монеты
            message_parts = [f"{exchange_string}\n{'💰 ' + coin.upper()}\n"]
            for platform, platform_data in coin_data['data'].items():
                # Добавляем информацию о платформе в сообщение
                message_parts.append(
                    f"{platform}: \n💲 Цена = {platform_data['price']} , \n📊 Объем (24h) = {platform_data['vol24']}\nСети:\n"
                )
                if 'network' in platform_data and platform_data['network'] is not None:
                    for network, network_data in platform_data['network'].items():
                        if network_data is not None:
                            # Получаем комиссию для каждой сети
                            fee = network_data.get('maxFee', network_data.get('minFee'))
                            message_parts.append(f"   {network} - комиссия = {fee}\n")
                        else:
                            # Если данных нет, добавляем сообщение об отсутствии данных
                            message_parts.append(f"   {network} - данные отсутствуют\n")
                else:
                    # Если данных о сети нет, добавляем сообщение об отсутствии данных
                    message_parts.append("   Данные о сети отсутствуют\n")
            # Добавляем разницу в котировках в сообщение
            message_parts.append(f"\n🎯 Разница цен: {coin_data['dif']}%\n")
            # Добавляем сообщение в список сообщений
            messages.append(''.join(message_parts))
    return messages
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    await update.effective_chat.send_message(
        "Не доступна помощь.\n"
        "Авторизуйтесь и продолжите работу."
    )
def main() -> None:
    """
    Главная функция, которая запускает бота.
    """
    # Создаем приложение и передаем токен
    application = Application.builder().token(TOKEN).build()
    # Обработчик команды "start"
    application.add_handler(CommandHandler("passauth", passauth))
    # Обработчик для текстовых сообщений, которые не являются командами и ответами
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.REPLY, password))

    # Обработчик команды "menu"
   # application.add_handler(CommandHandler("menu", menu))

    #application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.REPLY, button_handle))
    application.add_handler(MessageHandler(filters.Regex('^Запустить оповещения$|^Остановить оповещения$|'
                                                         '^Настройки$|^Запросить котировки$'), UiHandler.bh_start_menu))
    # Обработчик для кнопок
    #application.add_handler(CallbackQueryHandler(button))


    # Обработчик команды "help"
    application.add_handler(CommandHandler("help", help_command))
    # Инициализируем данные монет в контроллере
    asyncio.ensure_future(DH.ListCoins.initialize_data())
    # Запускаем бота до тех пор, пока пользователь не нажмет Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

