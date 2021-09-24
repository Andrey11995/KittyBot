import os
import sys
import requests
import logging
import telebot
from logging import StreamHandler
from telegram import ReplyKeyboardMarkup
from flask import Flask, request
from dotenv import load_dotenv


load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
APP_URL = 'https://kot0bot.herokuapp.com/'
API_URL = 'https://api.thecatapi.com/v1/images/search'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = StreamHandler(sys.stderr)
logger.addHandler(handler)

bot = telebot.TeleBot(token=TELEGRAM_TOKEN)
server = Flask(__name__)


@server.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '!', 200


@server.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    return '!', 200


def get_new_image():
    try:
        response = requests.get(API_URL).json()
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


    # updater = Updater(token=TELEGRAM_TOKEN)
    #
    # updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    # updater.dispatcher.add_handler(CommandHandler('newcat', new_cat))
    #
    # updater.start_polling()
    # updater.idle()


if __name__ == '__main__':
    server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    main()
