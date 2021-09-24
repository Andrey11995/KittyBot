import os
import sys
import requests
import logging

from logging import StreamHandler
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Updater

from dotenv import load_dotenv


load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = StreamHandler(sys.stderr)
logger.addHandler(handler)

URL = 'https://api.thecatapi.com/v1/images/search'


def get_new_image():
    try:
        response = requests.get(URL).json()
    except Exception as error:
        logger.warning('API котиков не отвечает!')
        logger.error(error)
        logger.info('Пытаемся запросить собачек')
        new_url = 'https://api.thedogapi.com/v1/images/search'
        response = requests.get(new_url).json()
    random_cat = response[0].get('url')
    return random_cat


def new_cat(update, context):
    try:
        chat = update.effective_chat
        context.bot.send_photo(chat.id, get_new_image())
        logger.info('Фото отправлено')
    except Exception as error:
        logger.error(f'Не удалось отправить сообщение! Ошибка: {error}')


def wake_up(update, context):
    try:
        chat = update.effective_chat
        name = update.message.chat.first_name
        button = ReplyKeyboardMarkup([['/newcat']], resize_keyboard=True)
        context.bot.send_message(
            chat_id=chat.id,
            text='Привет, {}. Посмотри, какого котика я тебе нашёл!'.format(name),
            reply_markup=button
        )
        context.bot.send_photo(chat.id, get_new_image())
        logger.info('Фото отправлено')
    except Exception as error:
        logger.error(f'Не удалось отправить сообщение! Ошибка: {error}')


def main():
    logger.debug('КотоБот запущен')
    updater = Updater(token=TELEGRAM_TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CommandHandler('newcat', new_cat))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
