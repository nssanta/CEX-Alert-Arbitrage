#!/usr/bin/env python
# pylint: disable=unused-argument

import logging
import asyncio

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, \
    ForceReply, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import filters, Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler

from Core.DataHandler import DataHandler
from exchange.BybitApi import BybitApi
from exchange.CoinWApi import CoinWApi
from exchange.OkxApi import OkxApi

#______________________________________________________________________________________________________________________
# СПИСОК КОНСТАНТ
# Токен бота
TOKEN = "6867257543:AAEzA4okBW2xLPN66Rz92Ghq9sFHZmfh9xo"
# Список кому доступен бот
WhiteList = [
    '6219851487',
    '6348339423'
]
# Пароль
PASSWORD = "AmadisLove"
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
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
            await update.message.reply_text('Пожалуйста, введите пароль', reply_markup=ForceReply())
        else:
            # Если пользователь не в белом списке, отправляем сообщение об ошибке
            await update.message.reply_text('Извините, вас нет в списке')
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
        await update.message.reply_text('Доступ разрешен')
    else:
        # Выводим сообщение об не удачной аутентификации
        await update.message.reply_text('Неверный пароль')
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
        Меню которое вызывается по команде /menu и содержит кнопки.
        :param update: Объект Update, содержащий информацию о текущем обновлении.
        :param context: Объект Context, содержащий информацию о текущем контексте.
        :return:
    """
    # Получаем ID пользователя
    user_id = update.effective_user.id
    # Получаем список авторизованных пользователей
    authorized_users = context.bot_data.setdefault('AUTHORIZED_USERS', [])
    # Проверяем есть ли пользователь в списке авторизованых
    if str(user_id) in authorized_users:
        # Создаем клавиатуру для меню
        keyboard = [
            [
                InlineKeyboardButton("Запустить оповещения", callback_data="1"),
                InlineKeyboardButton("Остановить оповещения", callback_data="2"),
            ],
            [InlineKeyboardButton("Запросить котировки", callback_data="3")],
        ]
        # Создаем разметку для клавиатуры
        reply_markup = InlineKeyboardMarkup(keyboard)
        # Отправляем сообщение с меню
        await update.message.reply_text("Пожалуйста выберите:", reply_markup=reply_markup)
    else:
        # Если пользователь не авторизован, отправляем сообщение об ошибке
        await update.message.reply_text('Извините, вы не авторизованы для использования этого меню')
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Функция обрабатывает нажатия кнопок в меню.
    :param update: Объект Update, содержащий информацию о текущем обновлении.
    :param context: Объект Context, содержащий информацию о текущем контексте.
    :return:
    """
    # Получаем ID пользователя
    user_id = update.effective_user.id
    # Получаем список авторизованных пользователей
    authorized_users = context.bot_data.setdefault('AUTHORIZED_USERS', [])
    # Получаем данные о нажатой кнопке
    query = update.callback_query
    if str(user_id) in authorized_users:
        # Отвечаем на запрос кнопки
        await query.answer()
        # Обрабатываем нажатие кнопки в зависимости от ее данных
        if query.data == "1":
            # Если пользователь нажал кнопку "Запустить оповещения"
            await update.effective_chat.send_message("Вы включили оповещения!")
            # Запускаем оповещения
            await start_alerts(update, context)
        elif query.data == "2":
            # Если пользователь нажал кнопку "Остановить оповещения"
            await update.effective_chat.send_message("Оповещения отключены!")
            # Останавливаем оповещения
            await stop_alerts(update, context)
        elif query.data == "3":
            # Если пользователь нажал кнопку "Запросить котировки"
            await update.effective_chat.send_message("Давай-давай пошел-пошел\nФункция находится в разработке.")
            # Запрашиваем котировки
            await request_quotes(update, context)
    else:
        # Если пользователь не авторизован, отправляем сообщение об ошибке
        await query.answer()
        await query.edit_message_text(text='Извините, вы не авторизованы для использования этого меню')
# async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """
#         Меню которое вызывается по команде /menu и содержит кнопки.
#         :param update: Объект Update, содержащий информацию о текущем обновлении.
#         :param context: Объект Context, содержащий информацию о текущем контексте.
#         :return:
#     """
#     # Получаем ID пользователя
#     user_id = update.effective_user.id
#     # Получаем список авторизованных пользователей
#     authorized_users = context.bot_data.setdefault('AUTHORIZED_USERS', [])
#     # Проверяем есть ли пользователь в списке авторизованых
#     if str(user_id) in authorized_users:
#         # Создаем клавиатуру для меню
#         keyboard = [
#             [
#                 KeyboardButton("Запустить оповещения", ),#callback_data="1"),
#                 KeyboardButton("Остановить оповещения", ),#callback_data="2"),
#             ],
#             [KeyboardButton("Запросить котировки", )],#callback_data="3")],
#         ]
#         # Создаем разметку для клавиатуры
#         reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
#         # Отправляем сообщение с меню
#         await update.message.reply_text("Пожалуйста выберите:", reply_markup=reply_markup)
#     else:
#         # Если пользователь не авторизован, отправляем сообщение об ошибке
#         await update.message.reply_text('Извините, вы не авторизованы для использования этого меню')
# async def button_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """
#     Функция обрабатывает нажатия кнопок в меню.
#     :param update: Объект Update, содержащий информацию о текущем обновлении.
#     :param context: Объект Context, содержащий информацию о текущем контексте.
#     :return:
#     """
#     # Получаем ID пользователя
#     user_id = update.effective_user.id
#     # Получаем список авторизованных пользователей
#     authorized_users = context.bot_data.setdefault('AUTHORIZED_USERS', [])
#     # Получаем данные о нажатой кнопке
#     query = update.callback_query
#     if str(user_id) in authorized_users:
#         # Отвечаем на запрос кнопки
#         await query.answer()
#         # Обрабатываем нажатие кнопки в зависимости от ее данных
#         if update.message.text == "Запустить оповещения":
#             # Если пользователь нажал кнопку "Запустить оповещения"
#             #await update.effective_chat.send_message("Вы включили оповещения!")
#             await update.message.reply_text("Вы включили оповещения!")
#             # Запускаем оповещения
#             await start_alerts(update, context)
#         elif update.message.text == "Остановить оповещения":
#             # Если пользователь нажал кнопку "Остановить оповещения"
#             await update.effective_chat.send_message("Оповещения отключены!")
#             # Останавливаем оповещения
#             await stop_alerts(update, context)
#         elif update.message.text == "Запросить котировки":
#             # Если пользователь нажал кнопку "Запросить котировки"
#             await update.effective_chat.send_message("Давай-давай пошел-пошел\nФункция находится в разработке.")
#             # Запрашиваем котировки
#             await request_quotes(update, context)
#     else:
#         # Если пользователь не авторизован, отправляем сообщение об ошибке
#         await query.answer()
#         await query.edit_message_text(text='Извините, вы не авторизованы для использования этого меню')
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
            await update.effective_chat.send_message("🚀")
            for msg in messages:
                await update.effective_chat.send_message(msg)
                await asyncio.sleep(2)
            # Пауза в секундах для всего блока уведомлений
            await asyncio.sleep(30)
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
    application.add_handler(CommandHandler("start", start))
    # Обработчик для текстовых сообщений, которые не являются командами и ответами
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.REPLY, password))
    # Обработчик команды "menu"
    application.add_handler(CommandHandler("menu", menu))
    # Обработчик для кнопок
    application.add_handler(CallbackQueryHandler(button))
    # Обработчик команды "help"
    application.add_handler(CommandHandler("help", help_command))
    # Инициализируем данные монет в контроллере
    asyncio.ensure_future(DH.ListCoins.initialize_data())
    # Запускаем бота до тех пор, пока пользователь не нажмет Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

