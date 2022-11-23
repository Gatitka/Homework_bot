import logging
import os

import requests
import sys
import telegram
import time
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler
from pprint import pprint

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s, %(levelname)s, %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

handler_rfh = RotatingFileHandler(
    'my_logger.log',
    maxBytes=50000000,
    backupCount=5
)
formatter = logging.Formatter('%(asctime)s, %(levelname)s, %(message)s')
handler_rfh.setFormatter(formatter)
logger.addHandler(handler_rfh)


def send_message(bot, message):
    """ Отправка сообщений ботом. Логирование каждого сообщения и ошибок
    в случае невозможности отправки сообщения."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(f'Бот отправил сообщение: {message}')
    except Exception as error:
        logger.error(f'Сбой при отправке сообщения ботом: '
                     f'{message}. Ошибка {error}')


def get_api_answer(current_timestamp):
    """Получение API ответа от эндпоинта."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        error_text = (f'Сбой в работе программы: Эндпоинт {ENDPOINT} '
                      f'недоступен. Код ответа API: {response.status_code}')
        if response.status_code != 200:
            raise Exception(error_text)
        else:
            response = response.json()
            pprint(response)
            return response
    except requests.exceptions.RequestException as e:
        raise error(e)


def check_response(response):
    """Проверка ответа API на корректность."""
    message = 'Начало проерки ответа сервера'
    logger.debug(message)
    if not isinstance(response, dict):
        message = 'Ответ от эндпоинта пришел не в формате словаря'
        raise TypeError(message)
    if 'homeworks' not in response:
        message = 'Данных homeworks нет в ответе эндпоинта'
        raise KeyError(message)
    if not response['current_date']:
        message = 'Данных current_date нет в ответе эндпоинта'
        raise KeyError(message)
    if not isinstance(response['current_date'], int):
        message = 'Данные current_date получены не в формате int'
        raise TypeError(message)

    homeworks = response['homeworks']
    if not isinstance(homeworks, list):
        message = 'Данные homeworks получены не в виде списка'
        raise TypeError(message)
    return homeworks


def parse_status(homework):
    """ Статус проверки домашней работы, полученный в API, ищется
    в словаре HOMEWORK_VERDICTS, возвращая значение по ключу-статусу."""
    if 'homework_name' not in homework:
        message = 'Данных homework_name нет в ответе эндпоинта'
        raise KeyError(message)
    if 'status' not in homework:
        message = 'Данных status нет в ответе эндпоинта'
        raise KeyError(message)
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status not in HOMEWORK_VERDICTS:
        message = 'Статус домашней работы не определен!'
        raise Exception(message)
    verdict = HOMEWORK_VERDICTS.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Доступность токенов."""
    if all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)) is True:
        return True
    else:
        return False


def main():
    """Основная логика работы бота."""
    if check_tokens() is False:
        logger.critical(
            'отсутствие обязательных переменных окружения',
            'во время запуска бота, бот остановлен'
        )
        quit()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    send_message(bot, 'Старт')
    current_timestamp = int(time.time())
    old_error = ''
    while True:
        try:
            response = get_api_answer(current_timestamp)
            current_timestamp = response.get('current_date')
            homeworks = check_response(response)
            if not homeworks:
                logger.debug("Статус домашней работы не изменился")
            else:
                message = parse_status(homeworks[0])
                logger.info(message)
                send_message(bot, message)
            send_message(bot, 'Пауза')

        except Exception as error:
            logger.error(error)
            if error != old_error:
                message = f'Сбой в работе программы: {error}'
                send_message(bot, message)
                old_error = error
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
