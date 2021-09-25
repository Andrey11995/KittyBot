import os
import sys
import requests
import logging
import telebot
from telebot import types
from flask import Flask, request
from logging import StreamHandler
from dotenv import load_dotenv


load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
APP_URL = f'https://kot0bot.herokuapp.com/{TELEGRAM_TOKEN}'
API_URL = 'https://api.thecatapi.com/v1/images/search'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = StreamHandler(sys.stderr)
logger.addHandler(handler)

bot = telebot.TeleBot(TELEGRAM_TOKEN)
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


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    send_cat = types.KeyboardButton('🐱 КОТИКИ')
    markup.add(send_cat)
    try:
        name = message.from_user.first_name
        bot.reply_to(
            message,
            'Привет, {}. Посмотри, какого котика я тебе нашёл!'.format(name),
            reply_markup=markup
        )
        bot.send_photo(message.chat.id, get_new_image())
        logger.info('Фото отправлено')
    except Exception as error:
        logger.error(f'Не удалось отправить сообщение! Ошибка: {error}')


@bot.message_handler(content_types=['text'])
def new_cat(message):
    try:
        if message.text == '🐱 КОТИКИ':
            bot.send_photo(message.chat.id, get_new_image())
            logger.info('Фото отправлено')
    except Exception as error:
        logger.error(f'Не удалось отправить фото! Ошибка: {error}')


def get_new_image():
    try:
        response = requests.get(API_URL).json()
    except Exception as error:
        logger.warning('API котиков не отвечает!')
        logger.error(error)
        logger.info('Пытаемся запросить собачек')
        new_url = 'https://api.thedogapi.com/v1/images/search'
        response = requests.get(new_url).json()
    random_image = response[0].get('url')
    return random_image


# def new_cat(update, context):
#     try:
#         chat = update.effective_chat
#         context.bot.send_photo(chat.id, get_new_image())
#         logger.info('Фото отправлено')
#     except Exception as error:
#         logger.error(f'Не удалось отправить сообщение! Ошибка: {error}')


def main():
    try:
        server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
        logger.debug('КотоБот запущен')
    except Exception as error:
        logger.critical(f'Ошибка при запуске сервера: {error}')


if __name__ == '__main__':
    main()

