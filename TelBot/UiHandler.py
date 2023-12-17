import logging
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes

from TelBot import UiBot
from TelBot.CallHandler import stop_alerts, request_quotes, start_alerts
from TelBot.Variable import SETTING_STATE, TIMER_SETTING_STATE, WORKING_STATE, SPREAD_SETTING_STATE, \
    INPUT_TIME_SETTING_STATE, INPUT_SPRED_SETTING_STATE, EXCHANGE_SETTING_STATE, INPUT_COINPAIR_SETTING_STATE, \
    VOLUME_SETTING_STATE, INPUT_VOLUME_SETTING_STATE

#   ЛОГИРОВАНИЕ В ФАЙЛ И КОНСОЛЬ!
log_file = "ui_handler.log"
logger = logging.getLogger("UiHandler")
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
async def bh_start_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
        Функция обрабатывает нажатия кнопок в главном меню.
        :param update: Объект Update, содержащий информацию о текущем обновлении.
        :param context: Объект Context, содержащий информацию о текущем контексте.
        :return:
    """
    try:
        # Получаем ID пользователя
        user_id = update.effective_user.id
        # Получаем список авторизованных пользователей
        authorized_users = context.bot_data.get('AUTHORIZED_USERS')
        # # Получаем данные о нажатой кнопке
        # query = update.callback_query
        # Переменая хранит текст отправленый пользователем.
        text = update.message.text
        if str(user_id) in authorized_users:
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
                return SETTING_STATE
            elif text == "Запросить котировки":
                await update.message.reply_text('Пожалуйста введите монетную в формате coincoin\n'
                                                'Две монеты слитно и без лишних знаков\n'
                                                'Примеры: btcustd , BTCUSDTC, ETHBTC, tonusdt',
                                                reply_markup=ReplyKeyboardRemove())
                return INPUT_COINPAIR_SETTING_STATE
        else:
            # Если пользователь не авторизован, отправляем сообщение об ошибке
            await update.message.reply_text('Извините, вы не авторизованы для использования этого меню',
                                           reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        logger.error(f"Возникла ошибка: {e} функция bh_start_menu")
async def bh_setting_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
        Функция обрабатывает нажатия кнопок в главном меню.
        :param update: Объект Update, содержащий информацию о текущем обновлении.
        :param context: Объект Context, содержащий информацию о текущем контексте.
        :return:
    """
    try:
        # Получаем ID пользователя
        user_id = update.effective_user.id
        # Получаем список авторизованных пользователей
        authorized_users = context.bot_data.get('AUTHORIZED_USERS')
        # Переменая хранит текст отправленый пользователем.
        text = update.message.text
        if str(user_id) in authorized_users:
            # Обрабатываем нажатие кнопки в зависимости от ее данных
            if text == "Таймер":
                await update.message.reply_text('Выберите или введите время периода оповещений',
                                                reply_markup=UiBot.keyboard_setting_timer(update, context))
                return TIMER_SETTING_STATE
            elif text == "Спред":
                await update.message.reply_text('Выберите или введите время mix-max спреда',
                                                reply_markup=UiBot.keyboard_setting_spread(update, context))
                return SPREAD_SETTING_STATE
            elif text == "Объем":
                await update.message.reply_text('Выберите объем',
                                                reply_markup=UiBot.keyboard_setting_volume(update, context))
                return VOLUME_SETTING_STATE
            elif text == "Биржи":
                await update.message.reply_text('Выберите биржи',
                                                reply_markup=UiBot.keyboard_setting_exchange(update, context))
                return EXCHANGE_SETTING_STATE
            elif text == "<- назад":
                await update.message.reply_text("Вы в главном меню", reply_markup=UiBot.keyboard_start_menu(update, context))
                return WORKING_STATE
        else:
            # Если пользователь не авторизован, отправляем сообщение об ошибке
            await update.message.reply_text('Извините, вы не авторизованы для использования этого меню',
                                            reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        logger.error(f"Возникла ошибка: {e} функция bh_setting_menu")
async def bh_setting_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
        Функция обрабатывает нажатия кнопок в меню настроек таймера.
        :param update: Объект Update, содержащий информацию о текущем обновлении.
        :param context: Объект Context, содержащий информацию о текущем контексте.
        :return:
    """
    try:
        # Получаем ID пользователя
        user_id = update.effective_user.id
        # Получаем список авторизованных пользователей
        authorized_users = context.bot_data.get('AUTHORIZED_USERS')
        # Переменая хранит текст отправленый пользователем.
        text = update.message.text

        if str(user_id) in authorized_users:
            # Обрабатываем нажатие кнопки в зависимости от ее данных
            if text == "30 секунд":
                context.chat_data['TIMER_ALERT'] = 30
                await update.message.reply_text('Таймер установлен на 30 секунд'
                                                '\nНе забудьте Отключить и Включить уведомления заново!!!',
                                                reply_markup=UiBot.keyboard_setting_menu(update, context))
                return SETTING_STATE
            elif text == "1 минута":
                context.chat_data['TIMER_ALERT'] = 60
                await update.message.reply_text('Таймер установлен на 1 минуту'
                                                '\nНе забудьте Отключить и Включить уведомления заново!!!',
                                                reply_markup=UiBot.keyboard_setting_menu(update, context))
                return SETTING_STATE
            elif text == "2 минуты":
                context.chat_data['TIMER_ALERT'] = 120
                await update.message.reply_text('Таймер установлен на 2 минуты'
                                                '\nНе забудьте Отключить и Включить уведомления заново!!!',
                                                reply_markup=UiBot.keyboard_setting_menu(update, context))
                return SETTING_STATE
            elif text == "5 минут":
                context.chat_data['TIMER_ALERT'] = 300
                await update.message.reply_text('Таймер установлен на 5 минут'
                                                '\nНе забудьте Отключить и Включить уведомления заново!!!',
                                                reply_markup=UiBot.keyboard_setting_menu(update, context))
                return SETTING_STATE
            elif text == "10 минут":
                context.chat_data['TIMER_ALERT'] = 600
                await update.message.reply_text('Таймер установлен на 10 минут'
                                                '\nНе забудьте Отключить и Включить уведомления заново!!!',
                                                reply_markup=UiBot.keyboard_setting_menu(update, context))
                return SETTING_STATE
            elif text == "Установить вручную":
                await update.message.reply_text('Пожалуйста, введите время в секундах от 30сек - 24 часов\n'
                                                'Надеюсь умеете считать не только крипту\n'
                                                'Введите например 45 или 10800 (это 3 часа)\n'
                                                'Формула: 3часа×60минут×60секунд = 10800секунд',
                                                reply_markup=ReplyKeyboardRemove())
                return INPUT_TIME_SETTING_STATE

            elif text == "<- назад":
                await update.message.reply_text('Меню настроек', reply_markup=UiBot.keyboard_setting_menu(update, context))
                return SETTING_STATE

        else:
            # Если пользователь не авторизован, отправляем сообщение об ошибке
            await update.message.reply_text('Извините, вы не авторизованы для использования этого меню',
                                            reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        logger.error(f"Возникла ошибка: {e} функция bh_setting_timer")
async def bh_setting_spreed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
        Функция обрабатывает нажатия кнопок в меню настроек таймера.
        :param update: Объект Update, содержащий информацию о текущем обновлении.
        :param context: Объект Context, содержащий информацию о текущем контексте.
        :return:
    """
    try:
        # Получаем ID пользователя
        user_id = update.effective_user.id
        # Получаем список авторизованных пользователей
        authorized_users = context.bot_data.get('AUTHORIZED_USERS')
        # Переменая хранит текст отправленый пользователем.
        text = update.message.text

        if str(user_id) in authorized_users:
            # Обрабатываем нажатие кнопки в зависимости от ее данных
            if text == "0.8 - 2.5":
                context.chat_data.get('DH_Class').set_min_max_spred(0.8, 2.5)
                await update.message.reply_text('Спред изменен',reply_markup=UiBot.keyboard_setting_menu(update, context))
                return SETTING_STATE
            elif text == "1 - 2.5":
                context.chat_data.get('DH_Class').set_min_max_spred(1, 2.5)
                await update.message.reply_text('Спред изменен', reply_markup=UiBot.keyboard_setting_menu(update, context))
                return SETTING_STATE
            elif text == "1.5 - 2.5":
                context.chat_data.get('DH_Class').set_min_max_spred(1.5, 2.5)
                await update.message.reply_text('Спред изменен', reply_markup=UiBot.keyboard_setting_menu(update, context))
                return SETTING_STATE
            elif text == "2 - 2.5":
                context.chat_data.get('DH_Class').set_min_max_spred(2, 2.5)
                await update.message.reply_text('Спред изменен', reply_markup=UiBot.keyboard_setting_menu(update, context))
                return SETTING_STATE
            elif text == "3 - 5":
                context.chat_data.get('DH_Class').set_min_max_spred(3, 5)
                await update.message.reply_text('Спред изменен', reply_markup=UiBot.keyboard_setting_menu(update, context))
                return SETTING_STATE
            elif text == "5 - 7":
                context.chat_data.get('DH_Class').set_min_max_spred(5, 7)
                await update.message.reply_text('Спред изменен', reply_markup=UiBot.keyboard_setting_menu(update, context))
                return SETTING_STATE
            elif text == "Установить вручную":
                await update.message.reply_text('Пожалуйста, введите спред вручную\nВводите два числа через пробел!\n'
                                                'Если число не целое, ОБЯЗАТЕЛЬНО используйте точку как разделитель\n'
                                                'Пример: 12 21.5\n'
                                                'Еще пример: 1.7 3.3',
                                                reply_markup=ReplyKeyboardRemove())
                return INPUT_SPRED_SETTING_STATE
            elif text == "<- назад":
                await update.message.reply_text('Меню настроек', reply_markup=UiBot.keyboard_setting_menu(update, context))
                return SETTING_STATE
        else:
            # Если пользователь не авторизован, отправляем сообщение об ошибке
            await update.message.reply_text('Извините, вы не авторизованы для использования этого меню',
                                            reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        logger.error(f"Возникла ошибка: {e} функция bh_setting_spread")
async def bh_setting_exchange(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
        Функция обрабатывает нажатия кнопок в меню настроек таймера.
        :param update: Объект Update, содержащий информацию о текущем обновлении.
        :param context: Объект Context, содержащий информацию о текущем контексте.
        :return:
    """
    try:
        # Получаем ID пользователя
        user_id = update.effective_user.id
        # Получаем список авторизованных пользователей
        authorized_users = context.bot_data.get('AUTHORIZED_USERS')
        # Получаем список с контекста
        exchange_list_in_context = context.chat_data.get('EXCHANGE_LIST')
        # Переменая хранит текст отправленый пользователем.
        text = update.message.text
        # Удалить символы "✅" и "❌" из текста
        text = text.replace("✅ ", "").replace("❌ ", "")
        if str(user_id) in authorized_users:
            if text == "<- назад":
                await update.message.reply_text('Меню настроек\nНе забудьте ОТКЛЮЧИТЬ и ВКЛЮЧИТЬ уведомления!!!',
                                                reply_markup=UiBot.keyboard_setting_menu(update, context))
                return SETTING_STATE
            else:
                # Найти биржу по имени и изменить значение is_selected
                for exchange in exchange_list_in_context:
                    if exchange.name in text:
                        exchange.is_selected = not exchange.is_selected
                        break

            await update.message.reply_text('Обновленый список',
                                            reply_markup=UiBot.keyboard_setting_exchange(update, context))
            return EXCHANGE_SETTING_STATE

    except Exception as e:
        logger.error(f"Возникла ошибка: {e} функция bh_setting_exchange")

async def bh_setting_volume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
        Функция обрабатывает нажатия кнопок в меню настроек объема.
        :param update: Объект Update, содержащий информацию о текущем обновлении.
        :param context: Объект Context, содержащий информацию о текущем контексте.
        :return:
    """
    try:
        # Получаем ID пользователя
        user_id = update.effective_user.id
        # Получаем список авторизованных пользователей
        authorized_users = context.bot_data.get('AUTHORIZED_USERS')
        # Переменая хранит текст отправленый пользователем.
        text = update.message.text

        if str(user_id) in authorized_users:
            # Обрабатываем нажатие кнопки в зависимости от ее данных
            if text == "10000":
                context.chat_data.get('DH_Class').set_ratate_volume(10000)
                await update.message.reply_text('Объем изменен',
                                                reply_markup=UiBot.keyboard_setting_menu(update, context))
                return SETTING_STATE
            elif text == "20000":
                context.chat_data.get('DH_Class').set_ratate_volume(20000)
                await update.message.reply_text('Объем изменен',
                                    reply_markup=UiBot.keyboard_setting_menu(update, context))
                return SETTING_STATE
            elif text == "30000":
                context.chat_data.get('DH_Class').set_ratate_volume(30000)
                await update.message.reply_text('Объем изменен',
                                                reply_markup=UiBot.keyboard_setting_menu(update, context))
                return SETTING_STATE
            elif text == "50000":
                context.chat_data.get('DH_Class').set_ratate_volume(50000)
                await update.message.reply_text('Объем изменен',
                                                reply_markup=UiBot.keyboard_setting_menu(update, context))
                return SETTING_STATE
            elif text == "100000":
                context.chat_data.get('DH_Class').set_ratate_volume(100000)
                await update.message.reply_text('Объем изменен',
                                                reply_markup=UiBot.keyboard_setting_menu(update, context))
                return SETTING_STATE
            elif text == "Установить вручную":
                await update.message.reply_text('Пожалуйста, введите объем вручную\n'
                                                'Пример: 15000\n'
                                                'Еще пример: 230000',
                                                reply_markup=ReplyKeyboardRemove())
                return INPUT_VOLUME_SETTING_STATE
            elif text == "<- назад":
                await update.message.reply_text('Меню настроек', reply_markup=UiBot.keyboard_setting_menu(update, context))
                return SETTING_STATE
        else:
            # Если пользователь не авторизован, отправляем сообщение об ошибке
            await update.message.reply_text('Извините, вы не авторизованы для использования этого меню',
                                            reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        logger.error(f"Возникла ошибка: {e} функция bh_setting_volume")