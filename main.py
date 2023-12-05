#!/usr/bin/env python
# pylint: disable=unused-argument

import logging
import asyncio

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ForceReply
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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
        Стартовая функция, которая проверяет белый список на доступ к боту, а также запрашивает пароль
        :param update:
        :param context:
        :return:
    """
    user = update.effective_user.id
    logger.info(f"user = {user}")
    if not str(user) in AUTHORIZED_USERS:
        if str(user) in WhiteList:
            await update.message.reply_text('Пожалуйста, введите пароль', reply_markup=ForceReply())
        else:
            await update.message.reply_text('Извините, вы не в белом списке')
    else:
        await update.message.reply_text('Вы уже авторизованы')


async def password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
        Функция которая вызывается для авторизованых пользователей, проверяет пароль и
        при авторизации добавляет id пользователя в AUTHORIZED_USERS, список который будет проверятся дальше.
        :param update:
        :param context:
        :return:
    """
    user = update.effective_user.id
    logger.info(f"update.message.text = {update.message.text}")
    if update.message.text == PASSWORD:
        await update.message.reply_text('Доступ разрешен')
        AUTHORIZED_USERS.append(str(user))
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        context.bot_data.setdefault('AUTHORIZED_USERS', []).append(str(user))
        #
    else:
        await update.message.reply_text('Неверный пароль')


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
        Меню которое вызывается по команде /menu и содержит кнопки.
        :param update:
        :param context:
        :return:
    """
    global AUTHORIZED_USERS
    user = update.effective_user.id
    logger.info(f"user in menu = {user} = {AUTHORIZED_USERS}")

    #if user in AUTHORIZED_USERS:

    if str(user) in context.bot_data.get('AUTHORIZED_USERS', []):
        #
        keyboard = [
            [
                InlineKeyboardButton("Запустить оповещения", callback_data="1"),
                InlineKeyboardButton("Остановить оповещения", callback_data="2"),
            ],
            [InlineKeyboardButton("Запросить котировки", callback_data="3")],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("Пожалуйста выберите:", reply_markup=reply_markup)
    else:
        await update.message.reply_text('Извините, вы не авторизованы для использования этого меню')


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    user = update.effective_user

    if str(user.id) in AUTHORIZED_USERS:
        await query.answer()

        if query.data == "1":
            await update.effective_chat.send_message("+++++ ВЫ ВКЛЮЧИЛИ УВЕДОМЛЕНИЯ!")

            await start_alerts(update, context)
        elif query.data == "2":
            await update.effective_chat.send_message("------ ВЫ ВЫКЛЮЧИЛИ УВЕДОМЛЕНИЯ!")
            await stop_alerts(update, context)
        elif query.data == "3":
            await update.effective_chat.send_message("Давай-давай пошел-пошел\nФункция находится в разработке.")
            await request_quotes(update, context)
    else:
        await query.answer()
        await query.edit_message_text(text='Извините, вы не авторизованы для использования этого меню')

async def alerts_loop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    while True:
        # # Запрашиваем данные с апи
        # data_api = await DH.get_best_ticker(ex_list)
        # message = format_data(data_api)
        # await update.message.reply_text(message)
        # await asyncio.sleep(60)  # Пауза в 1 минут
    # Запрашиваем данные с апи
        logger.info("ждем оповещения 1")
        data_api = await DH.get_best_ticker(ex_list)
        logger.info(f"ждем оповещения 2 = {data_api}")
        messages = await format_data(data_api)
        for msg in messages:
            await update.effective_chat.send_message(msg)
            await asyncio.sleep(2)
       # await update.message.reply_text(message)
        logger.info("ждем оповещения 4")
        await asyncio.sleep(30)  # Пауза в 1 минут

async def start_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global ALERT_TASK
    if ALERT_TASK is not None:
        await update.message.reply_text('Оповещения уже запущены')
        return
    ALERT_TASK = asyncio.create_task(alerts_loop(update, context))


async def stop_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global ALERT_TASK
    if ALERT_TASK is None:
        await update.message.reply_text('Оповещения уже остановлены')
        return
    ALERT_TASK.cancel()
    ALERT_TASK = None


async def request_quotes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Функция в разработке, не спешите.')
    pass

async def format_data(data):
    messages = []
    for exchange, coins in data.items():
        logger.info(f"Processing exchange: {exchange}")
        for coin, coin_data in coins.items():
            logger.info(f"Processing coin: {coin}")
            message_parts = [f"{exchange}\n{coin}\n"]
            for platform, platform_data in coin_data['data'].items():
                logger.info(f"Processing platform: {platform}")
                message_parts.append(
                    f"{platform}: price = {platform_data['price']} , vol24 = {platform_data['vol24']}\nСети:\n"
                )
                if 'network' in platform_data and platform_data['network'] is not None:
                    for network, network_data in platform_data['network'].items():
                        if network_data is not None:
                            fee = network_data.get('maxFee', network_data.get('minFee'))
                            message_parts.append(f"{network} - комиссия = {fee}\n")
                        else:
                            logger.warning(f"Empty data for network: {network} in platform: {platform}")
                            message_parts.append(f"{network} - данные отсутствуют\n")
                else:
                    logger.warning(f"No network data found in platform: {platform}")
                    message_parts.append("Данные о сети отсутствуют\n")
            message_parts.append(f"\nРазница котировок составляет = {coin_data['dif']}\n")
            messages.append(''.join(message_parts))
    return messages


# async def format_data(data):
#     messages = []
#     for exchange, coins in data.items():
#         logger.info(f"Processing exchange: {exchange}")
#         for coin, coin_data in coins.items():
#             logger.info(f"Processing coin: {coin}")
#             message_parts = [f"{exchange}\n{coin}\n"]
#             for platform, platform_data in coin_data['data'].items():
#                 logger.info(f"Processing platform: {platform}")
#                 message_parts.append(
#                     f"{platform}: price = {platform_data['price']} , vol24 = {platform_data['vol24']}\nСети:\n"
#                 )
#                 for network, network_data in platform_data['network'].items():
#                     logger.info(f"Processing network: {network}")
#                     fee = network_data.get('maxFee', network_data.get('minFee'))
#                     message_parts.append(f"{network} - комиссия = {fee}\n")
#             message_parts.append(f"\nРазница котировок составляет = {coin_data['dif']}\n")
#             messages.append(''.join(message_parts))
#     return "\n".join(messages)


# async def format_data(data):
#     messages = []
#     for exchange, coins in data.items():
#         logger.info(f"{exchange} {coins}")
#         for coin, coin_data in coins.items():
#             logger.info(f"{coin} {coin_data}")
#             message = f"{exchange}\n{coin}\n"
#             for platform, platform_data in coin_data['data'].items():
#                 message += f"{platform}: price = {platform_data['price']} , vol24 = {platform_data['vol24']}\nСети:\n"
#                 for network, network_data in platform_data['network'].items():
#                     fee = network_data.get('maxFee', network_data.get('minFee'))
#                     message += f"{network} - комиссия = {fee}\n"
#             message += f"\nРазница котировок составляет = {coin_data['dif']}\n"
#             messages.append(message)
#     return "\n".join(messages)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    await update.message.reply_text(
        "Не доступна помощь.\n"
        "Авторизуйтесь и продолжите работу."
    )



def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()
      #
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.REPLY, password))
      # Меню
    application.add_handler(CommandHandler("menu", menu))
      # Кнопки
    application.add_handler(CallbackQueryHandler(button))
      # Помощь
    application.add_handler(CommandHandler("help", help_command))
    # ИНИЦИЛИРУЕМ ДАННЫЕ МОНЕТ В КОНТРОЛЛЕРЕ
    #await DH.ListCoins.initialize_data()
    asyncio.ensure_future(DH.ListCoins.initialize_data())

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    #asyncio.run(application.run_polling(allowed_updates=Update.ALL_TYPES))


if __name__ == "__main__":
    main()
