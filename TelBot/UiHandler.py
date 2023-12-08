from telegram import Update
from telegram.ext import ContextTypes

from TelBot import UiBot
from main import start_alerts, stop_alerts, request_quotes


async def bh_start_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
        Функция обрабатывает нажатия кнопок в главном меню.
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
    # Переменая хранит текст отправленый пользователем.
    text = update.message.text
    if str(user_id) in authorized_users:
        # Отвечаем на запрос кнопки
        # Обрабатываем нажатие кнопки в зависимости от ее данных
        if text == "Запустить оповещения":
            # Запускаем оповещения
            await start_alerts(update, context)
        elif text == "Остановить оповещения":
            # Останавливаем оповещения
            await stop_alerts(update, context)
        elif text == "Настройки":
            await update.message.reply_text('Выберите опцию настройки',
                                            reply_markup=UiBot.keyboard_setting_menu(update, context))
        elif text == "Запросить котировки":
            # Запрашиваем котировки
            await request_quotes(update, context)
    else:
        # Если пользователь не авторизован, отправляем сообщение об ошибке
        await query.edit_message_text(text='Извините, вы не авторизованы для использования этого меню')