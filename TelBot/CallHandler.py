import asyncio
import re

import logging
from telegram import Update
from telegram.ext import ContextTypes

from TelBot import Variable, UiBot
from TelBot.Variable import SETTING_STATE, WORKING_STATE

#   ЛОГИРОВАНИЕ В ФАЙЛ И КОНСОЛЬ!
log_file = "call_handler.log"
logger = logging.getLogger("CallHandler")
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

async def format_data_for_coin_pair(data):
    """
        Функция для форматирования данных, полученных от API, в сообщения для отправки на "Запросить котировки"
        :param data: Данные, полученные от API.
        :return: Список сообщений для отправки.
    """
    # # Создаем пустую строку для хранения результата
    # result = ''
    # # Проходим по всем элементам в данных
    # for item in data:
    #     # Каждый элемент в данных - это словарь, где ключ - это имя биржи
    #     for exchange, exchange_data in item.items():
    #         # Добавляем информацию о бирже в результат
    #         result += f'{exchange}:\n'
    #         result += f'💲 Цена = {exchange_data["price"]},\n'
    #         result += f'📊 Объем (24h) = {exchange_data["vol24"]}\n'
    #         result += 'Разница:\n'
    #
    #         # Добавляем информацию о разнице в результат
    #         for dif, value in exchange_data['dif'].items():
    #             result += f'   {dif}: {value}\n'
    #         # Добавляем пустую строку между биржами для лучшей читаемости
    #         result += '\n'
    #     logger.error(f"RES = {result}")
    # # Возвращаем итоговый результат
    # return result
    # Создаем пустой список для хранения сообщений
    messages = []
    # Проходим по всем элементам в данных
    for item in data:
        # Каждый элемент в данных - это словарь, где ключ - это имя биржи
        for exchange, exchange_data in item.items():
            # Создаем сообщение для текущей биржи
            message = f'{exchange}:\n'
            message += f'💲 Цена = {exchange_data["price"]},\n'
            message += f'📊 Объем (24h) = {exchange_data["vol24"]}\n'
            message += 'Разница:\n'
            # Добавляем информацию о разнице в сообщение
            for dif, value in exchange_data['dif'].items():
                message += f'   {dif}: {value}\n'
            # Добавляем сообщение в список сообщений
            messages.append(message)
    # Возвращаем список сообщений
    return messages
async def format_data_ticker(data):
    """
        Функция для форматирования данных, полученных от API, в сообщения для отправки.
        :param data: Данные, полученные от API.
        :return: Список сообщений для отправки.
    """
    messages = []
    try:
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
                        f"\n{platform}: \n💲 Цена = {platform_data['price']} , \n📊 Объем (24h) = {platform_data['vol24']}\nСети:\n"
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

    except Exception as e:
        logger.error(f"Возникла ошибка: {e} функция format_data_ticker")
        return []



async def password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
        Функция которая вызывается для авторизованых пользователей, проверяет пароль и
        при Аутентификации добавляет id пользователя в AUTHORIZED_USERS, список который будет проверятся дальше.
        :param update: Объект Update, содержащий информацию о текущем обновлении.
        :param context: Объект Context, содержащий информацию о текущем контексте.
        :return:
    """

    # Получаем ID пользователя
    user = update.effective_user.id
    try:
        # Проверяем ответ пользователя, правильно ли он ввел пароль
        if update.message.text == Variable.PASSWORD:
            # Добавляем ID пользователя в сессию бота
           # context.bot_data.setdefault('AUTHORIZED_USERS', []).append(str(user))
            context.bot_data['AUTHORIZED_USERS'].append(str(user))
            # Выводим сообщение об удачной аутентификации
            await update.message.reply_text('Доступ разрешен.\nДальнейшее управление через интерактивное меню.\n'
                                            'Если возникнут проблемы или зависание попробуй /help ',
                                            reply_markup=UiBot.keyboard_start_menu(update, context))
            return Variable.WORKING_STATE
        else:
            # Выводим сообщение об не удачной аутентификации
            await update.message.reply_text('Неверный пароль')
            return Variable.PASS_STATE
    except Exception as e:
        logger.error(f"Возникла ошибка: {e} функция password")

#_______________________________________________________________________________________________________________________
#                               Функции для оповещений
async def start_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
        Функция включает уведомления
        :param update: Объект Update, содержащий информацию о текущем обновлении.
        :param context: Объект Context, содержащий информацию о текущем контексте.
        :return:
    """
    try:
        # Проверяем, запущены ли уже оповещения
        if 'ALERT_TASK' in context.chat_data and context.chat_data['ALERT_TASK'] is not None:
            await update.effective_chat.send_message('Оповещения уже запущены')
            return
        # Сообщаем пользователю
        await update.message.reply_text("Вы включили оповещения!")
        # Запускаем цикл оповещений
        context.chat_data['ALERT_TASK'] = asyncio.create_task(alerts_loop(update, context))
    except Exception as e:
        logger.error(f"Возникла ошибка: {e} функция start_alerts")
async def stop_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
        Функция выключает уведомления
        :param update: Объект Update, содержащий информацию о текущем обновлении.
        :param context: Объект Context, содержащий информацию о текущем контексте.
        :return:
    """
    try:
        # Проверяем, остановлены ли уже оповещения
        if 'ALERT_TASK' not in context.chat_data or context.chat_data['ALERT_TASK'] is None:
            await update.effective_chat.send_message('Оповещения уже остановлены')
            return
        # Сообщаем пользователю
        await update.effective_chat.send_message("Оповещения отключены!")
        # Останавливаем цикл оповещений
        context.chat_data['ALERT_TASK'].cancel()
        context.chat_data['ALERT_TASK'] = None
    except Exception as e:
        logger.error(f"Возникла ошибка: {e} функция stop_alert")
async def alerts_loop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
        Функция которая делает уведомления у нее бесконечный цикл, управляется через переменную
        ALERT_TASK - которая является Task async
        :param update: Объект Update, содержащий информацию о текущем обновлении.
        :param context: Объект Context, содержащий информацию о текущем контексте.
        :return:
    """
    EXCHANGE_LIST = context.chat_data.get('EXCHANGE_LIST')
    selected_exchanges = [exchange for exchange in EXCHANGE_LIST if exchange.is_selected]
    while True:
        try:
            # Переменая хранит время паузы
            timer = context.chat_data.get('TIMER_ALERT')
            # Запрашиваем данные с API
            data_api = await context.chat_data.get('DH_Class').get_best_ticker(selected_exchanges)
            # Форматируем данные для отправки
            messages = await format_data_ticker(data_api)
            # Проверяем есть ли ответ от апи
            if messages:
                await update.effective_chat.send_message("🚀")
            else:
                await update.effective_chat.send_message("🌌")
            # Отправляем каждое сообщение с задержкой 2 секунды
            for msg in messages:
                await update.effective_chat.send_message(msg)
                await asyncio.sleep(2)
            # Пауза в секундах для всего блока уведомлений
            await asyncio.sleep(int(timer))
        except Exception as e:
            logger.error(f"Возникла ошибка: {e} функция alert_loop")
            continue
#_______________________________________________________________________________________________________________________

#_______________________________________________________________________________________________________________________
#                               Функции которые вызываются через кнопки меню настроек
async def request_quotes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await update.effective_chat.send_message('Функция в разработке, не спешите.')
    except Exception as e:
        logger.error(f"Возникла ошибка: {e} функция request_quotes")

async def input_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
        Функция проверяет текст введеный пользователем для установки таймера
        :param update: Объект Update, содержащий информацию о текущем обновлении.
        :param context: Объект Context, содержащий информацию о текущем контексте.
        :return:
    """
    try:
        # Получаем ID пользователя
        user = update.effective_user.id
        # Получаем ответ пользователя
        text = update.message.text
        if text.isdigit():
            number = int(text)
            # Проверяем диапозон от 30сек - 24 часов
            if 30 <= number <= 24 * 60 * 60:
                context.chat_data['TIMER_ALERT'] = number
                await update.message.reply_text(f'Таймер установлен на {number} секунд'
                                                f'\nНе забудьте Отключить и Включить уведомления заново!!!',
                                                reply_markup=UiBot.keyboard_setting_menu(update, context))
                return SETTING_STATE
            else:
                await update.message.reply_text(f'Не возможно установить таймер на {number} секунд\n'
                                                f'Правильный диапозон от 30 секунд до 24 часов!!!',
                                                reply_markup=UiBot.keyboard_setting_menu(update, context))
                return SETTING_STATE
        else:
            await update.message.reply_text(f'Число должно быть целым и без лишних знаков\nВведите целое число!!!',
                                            reply_markup=UiBot.keyboard_setting_menu(update, context))
            return SETTING_STATE
    except Exception as e:
        logger.error(f"Возникла ошибка: {e} функция input_timer")
async def input_spred(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
        Функция проверяет текст введенный пользователем для установки спреда в формате (float float)-число пробел число
        :param update: Объект Update, содержащий информацию о текущем обновлении.
        :param context: Объект Context, содержащий информацию о текущем контексте.
        :return:
    """
    try:
        # Получаем ID пользователя
        user = update.effective_user.id
        # Получаем ответ пользователя
        text = update.message.text
        # Разделяем ввод пользователя на две части по пробелу
        numbers = text.split()
        if len(numbers) == 2:
            # Преобразуем числа из строкового формата в числа с плавающей запятой
            min = float(numbers[0])
            max = float(numbers[1])
            # Проверяем, находятся ли числа в указанном диапазоне от 0.1 до 100 и чтобы второе число было больше первого
            if 0.1 <= min <= 100 and 0.1 <= max <= 100 and max > min:
                context.chat_data.get('DH_Class').set_min_max_spred(min, max)
                await update.message.reply_text(f'Спред изменен на диапозон от {min} до {max}',
                                                reply_markup=UiBot.keyboard_setting_menu(update, context))
                return SETTING_STATE
    except Exception as e:
        logger.error(f"Возникла ошибка: {e} функция input_timer")
async def input_coin_pair(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
        Функция проверяет текст введенный пользователем для запроса котировок по конкретной монете.
        :param update: Объект Update, содержащий информацию о текущем обновлении.
        :param context: Объект Context, содержащий информацию о текущем контексте.
        :return:
    """
    try:
        # Получаем ID пользователя
        user = update.effective_user.id
        # Получаем ответ пользователя
        text = update.message.text
        # Удаляем все лишнее и в lower case
        text = re.sub(r'\W+', ' ', text).lower()
        # Получаем список выбраных бирж у пользователя
        EXCHANGE_LIST = context.chat_data.get('EXCHANGE_LIST')
        selected_exchanges = [exchange for exchange in EXCHANGE_LIST if exchange.is_selected]
        # Запрашиваем данные с API
        data_api = await context.chat_data.get('DH_Class').get_coin_all_exchange(ex_list=selected_exchanges, coin_pair=text)
        # Форматируем данные для отправки
        messages = await format_data_for_coin_pair(data_api)
        # Проверяем есть ли ответ от апи
        if messages:
            # Отправляем каждое сообщение с задержкой 1 секунду
            for msg in messages:
                await update.effective_chat.send_message(msg)
                await asyncio.sleep(0.5)
            await update.message.reply_text(f'Можете запросить снова!',
                                            reply_markup=UiBot.keyboard_start_menu(update, context))
            return WORKING_STATE
        else:

            await update.message.reply_text(f'Данные не получены"',
                                            reply_markup=UiBot.keyboard_start_menu(update, context))
            return WORKING_STATE
    except Exception as e:
        logger.error("Данные не получены")
        await update.message.reply_text(f'Данные не получены\n'
                                        f'1) Попробуйте поменять монеты местами\n'
                                        f'2) Попробуйте отключить какую-нибудь биржу(биржи)',
                                        reply_markup=UiBot.keyboard_start_menu(update, context))
        return WORKING_STATE
#_______________________________________________________________________________________________________________________