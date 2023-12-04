#!/usr/bin/env python
# pylint: disable=unused-argument

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ForceReply
from telegram.ext import filters, Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler

# Константы
TOKEN = "6867257543:AAEzA4okBW2xLPN66Rz92Ghq9sFHZmfh9xo"
WhiteList = [
    '6219851487'
]
PASSWORD = "Amadis"
AUTHORIZED_USERS = []

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Sends a message with three inline buttons attached."""
#     user = update.effective_user
#     keyboard = [
#         [
#             InlineKeyboardButton("Запустить оповещения", callback_data="1"),
#             InlineKeyboardButton("Остановить оповещения", callback_data="2"),
#         ],
#         [InlineKeyboardButton("Запросить котировки", callback_data="3")],
#     ]
#
#     reply_markup = InlineKeyboardMarkup(keyboard)
#
#     await update.message.reply_text("Пожалуйста выберите:", reply_markup=reply_markup)
#
#
# async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Parses the CallbackQuery and updates the message text."""
#     query = update.callback_query
#
#     # CallbackQueries need to be answered, even if no notification to the user is needed
#     # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
#     await query.answer()
#
#     await query.edit_message_text(text=f"Selected option: {query.data}")
#
#
# async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Displays info on how to use the bot."""
#     await update.message.reply_text("Авторизуйтесь и введите /start")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
        Стартовая функция, которая проверяет белый список на доступ к боту, а также запрашивает пароль
        :param update:
        :param context:
        :return:
    """
    user = update.effective_user.id
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
    if update.message.text == PASSWORD:
        await update.message.reply_text('Доступ разрешен')
        AUTHORIZED_USERS.append(str(user))
    else:
        await update.message.reply_text('Неверный пароль')

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user.id
    if str(user) in AUTHORIZED_USERS:
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
        # CallbackQueries need to be answered, even if no notification to the user is needed
        # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
        await query.answer()

        if query.data == "1":
            await start_alerts(update, context)
        elif query.data == "2":
            await stop_alerts(update, context)
        elif query.data == "3":
            await request_quotes(update, context)
    else:
        await query.answer()
        await query.edit_message_text(text='Извините, вы не авторизованы для использования этого меню')

async def start_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Здесь ваш код для запуска оповещений
    pass

async def stop_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Здесь ваш код для остановки оповещений
    pass

async def request_quotes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Здесь ваш код для запроса котировок
    pass


# async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Parses the CallbackQuery and updates the message text."""
#     query = update.callback_query
#     user = update.effective_user.id
#
#     if str(user) in AUTHORIZED_USERS:
#         # CallbackQueries need to be answered, even if no notification to the user is needed
#         # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
#         await query.answer()
#
#         await query.edit_message_text(text=f"Selected option: {query.data}")
#     else:
#         await query.answer()
#         await query.edit_message_text(text='Извините, вы не авторизованы для использования этого меню')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    await update.message.reply_text("Use /start to test this bot.")
def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.REPLY, password))

    application.add_handler(CommandHandler("menu", menu))

    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("help", help_command))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()