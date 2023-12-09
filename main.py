#!/usr/bin/env python3

import os
import logging

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import filters, Application, CommandHandler, ContextTypes, MessageHandler, \
    ConversationHandler

from TelBot import UiHandler, CallHandler, Variable, UiBot


#TOKEN = os.getenv('bot_token')#environ.get("bot_token")
TOKEN = "os.getenv('TELEGRAM_BOT_TOKEN')"
#______________________________________________________________________________________________________________________


# Вывод логирования в терминал
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# выводим get и post
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
async def passauth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
        Стартовая функция, которая проверяет белый список на доступ к боту, а также запрашивает пароль
        :param update: Объект Update, содержащий информацию о текущем обновлении.
        :param context: Объект Context, содержащий информацию о текущем контексте.
        :return:
    """
    # Вызываем функцию которая инициализирует стартовые переменные. Только один раз при ссесии пользователя.
    if not context.chat_data.get('INITIALIZED'):
        await Variable.initialize_variables(update, context)
    # Получаем ID пользователя
    user_id = update.effective_user.id
    # Получаем список авторизованных пользователей
    authorized_users = context.bot_data.get('AUTHORIZED_USERS') #context.bot_data.setdefault('AUTHORIZED_USERS', [])
    # Проверяем, авторизован ли пользователь
    if str(user_id) not in authorized_users:
        # Если пользователь в белом списке, запрашиваем пароль
        if str(user_id) in Variable.WhiteList:
            await update.message.reply_text('Пожалуйста, введите пароль', reply_markup=ReplyKeyboardRemove())
            return Variable.PASS_STATE
        else:
            # Если пользователь не в белом списке, отправляем сообщение об ошибке
            await update.message.reply_text('Извините, вас нет в списке', reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
    else:
        # Если пользователь уже авторизован, отправляем сообщение об этом
        await update.message.reply_text('Вы уже авторизованы')
        return ConversationHandler.END
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
        Функция будет использоватся только для авторизованых пользователей,
        и пробовать выкинуть в главное меню (если возникнут баги)
        :param update: Объект Update, содержащий информацию о текущем обновлении.
        :param context: Объект Context, содержащий информацию о текущем контексте.
        :return:
    """
    # Получаем ID пользователя
    user_id = update.effective_user.id
    # Получаем список авторизованных пользователей
    authorized_users = context.bot_data.get('AUTHORIZED_USERS')  # context.bot_data.setdefault('AUTHORIZED_USERS', [])
    # Проверяем, авторизован ли пользователь
    if str(user_id) in authorized_users:
        await update.message.reply_text('Столкнулся с багом? Понимаю... Перезапускаю UI\n'
                                        'Пробуй дальнейшее управление через интерактивное меню.',
                                        reply_markup=UiBot.keyboard_start_menu(update, context))
        return Variable.WORKING_STATE

def main() -> None:
    """
    Главная функция, которая запускает бота.
    """
    # Создаем приложение и передаем токен
    application = Application.builder().token(TOKEN).build()

    # Фильтр для обработки сообщений в настроке бирж
    #exchange_names = "|".join(exchange.name for exchange in EXCHANGE_LIST)
    exchange_names= "Okx|Bybit|Coin W"
    exchange_filter = filters.Regex(f"^(✅|❌) ({exchange_names})$|^<- назад$")

    # Создаем обработчик состояний диалога
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('passauth', passauth)],
        states={
            Variable.PASS_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND & filters.REPLY, CallHandler.password)],

            Variable.AUTH_STATE: [CommandHandler('passauth', passauth)],

            Variable.WORKING_STATE: [MessageHandler(filters.Regex('^Запустить оповещения$|^Остановить оповещения$|'
                                                         '^Настройки$|^Запросить котировки$'), UiHandler.bh_start_menu)],

            Variable.SETTING_STATE: [MessageHandler(filters.Regex('^Таймер$|^Спред$|^Биржи$|'
                                                         '^Монеты$|^<- назад$'), UiHandler.bh_setting_menu)],

            Variable.TIMER_SETTING_STATE: [MessageHandler(filters.Regex('^30 секунд$|^1 минута$|'
            '^2 минуты$|^5 минут$|^10 минут$|^Установить вручную$|^<- назад$'), UiHandler.bh_setting_timer)],

            Variable.SPREAD_SETTING_STATE: [MessageHandler(filters.Regex('^0.5 - 2.5$|^0.6 - 2.5$|^0.7 - 2.5$|'
            '^0.8 - 2.5$|^0.9 - 2.5$|^1 - 2.5$|^Установить вручную$|^<- назад$'), UiHandler.bh_setting_spreed)],

            Variable.INPUT_TIME_SETTING_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND & filters.REPLY,
                                                              CallHandler.input_timer)],
            Variable.INPUT_SPRED_SETTING_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND & filters.REPLY,
                                                               CallHandler.input_spred)],


            Variable.EXCHANGE_SETTING_STATE: [MessageHandler(exchange_filter, UiHandler.bh_setting_exchange)]
        },
        fallbacks=[CommandHandler('help', help_command)],# заменить на что то более нужное в данном случае
    )
    # Добавляем обработчика состояний
    application.add_handler(conversation_handler)
    # # Инициализируем данные монет в контроллере
    # asyncio.ensure_future(context.chat_data.get('DH_Class').ListCoins.initialize_data())
    # Запускаем бота до тех пор, пока пользователь не нажмет Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

# Обработчик команды "start"
    #application.add_handler(CommandHandler("passauth", passauth))
    # Обработчик для текстовых сообщений, которые не являются командами и ответами
    #application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.REPLY, password))
    # Обработчик команды "menu"
   # application.add_handler(CommandHandler("menu", menu))
    #application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.REPLY, button_handle))
# Обработчик для кнопок
# application.add_handler(CallbackQueryHandler(button))
