import os
import sys
import requests
import telebot
import logging
from telebot import types
from telegram import Message
from flask import Flask, request
from logging import StreamHandler
from typing import Tuple
from dotenv import load_dotenv


load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = StreamHandler(sys.stderr)
logger.addHandler(handler)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
APP_URL = f'https://kot0bot.herokuapp.com/{TELEGRAM_TOKEN}'
CAT_API = 'https://api.thecatapi.com/v1/images/search'
DOG_API = 'https://api.thedogapi.com/v1/images/search'

sad_cat_url = ('https://avatars.yandex.net/get-music-user-playlist/34120/'
               '546136583.1000.75797/m1000x1000?1546676930515&webp=false')
sad_dog_url = ('https://avatars.mds.yandex.net/get-zen_doc/1898210/pub_5dcc'
               'fee9d2bc1447e8b05424_5dccff4bcd7152643c8dc951/scale_1200')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
server = Flask(__name__)


@server.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def get_message() -> Tuple[str, int]:
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '!', 200


@server.route('/')
def webhook() -> Tuple[str, int]:
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    return '!', 200


@bot.message_handler(commands=['start'])
def start(message: Message) -> None:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    cat_button = types.InlineKeyboardButton('🐱 Хочу КОТИКА 🐱')
    dog_button = types.InlineKeyboardButton('🐶 Хочу СОБАЧКУ 🐶')
    how_are_you_button = types.InlineKeyboardButton('😊 Как дела? 😊')
    markup.add(cat_button, dog_button, how_are_you_button)
    try:
        name = message.from_user.first_name
        bot.reply_to(
            message,
            ('Привет, {}\n\n'
             'Я - КотоБот.\n'
             'Я здесь для того, чтобы отправлять тебе фото '
             'котиков и собачек по запросу'.format(name)),
            reply_markup=markup
        )
        bot.send_message(message.chat.id, 'Для начала лови первого котика!')
        bot.send_photo(message.chat.id, get_new_cat(message))
        logger.info('Фото отправлено')
    except Exception as error:
        logger.error(f'Не удалось отправить сообщение! Ошибка: {error}')


@bot.message_handler(content_types=['text'])
def send_message(message: Message) -> None:
    try:
        if message.text == '🐱 Хочу КОТИКА 🐱':
            bot.send_photo(message.chat.id, get_new_cat(message))
            logger.info('Фото котика отправлено')
        elif message.text == '🐶 Хочу СОБАЧКУ 🐶':
            bot.send_photo(message.chat.id, get_new_dog(message))
            logger.info('Фото собачки отправлено')
        elif message.text == '😊 Как дела? 😊':
            markup = types.InlineKeyboardMarkup(row_width=2)
            good = types.InlineKeyboardButton(
                'Тоже норм',
                callback_data='good'
            )
            bad = types.InlineKeyboardButton(
                'Ну, такое...',
                callback_data='bad'
            )
            markup.add(good, bad)
            bot.send_message(
                message.chat.id,
                'Норм, твои как?',
                reply_markup=markup
            )
    except Exception as error:
        logger.error(f'Не удалось отправить сообщение! Ошибка: {error}')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call) -> None:
    try:
        if call.message:
            if call.data == 'good':
                text = 'Ну и отлично!\nКого тебе?\nКотика или собачку?'
                bot.send_message(call.message.chat.id, text)
            elif call.data == 'bad':
                text = ('Ничего, все наладится!\n'
                        'Давай скину котика или собачку?')
                bot.send_message(call.message.chat.id, text)
    except Exception as error:
        logger.error(f'Не удалось ответить на сообщение! Ошибка: {error}')


def get_new_cat(message: Message) -> str:
    try:
        response = requests.get(CAT_API).json()
        random_image = response[0].get('url')
        return random_image
    except Exception as error:
        logger.warning('API котиков не отвечает!')
        logger.error(f'Ошибка: {error}')
        text = ('К сожалению сервер котиков сейчас недоступен...\n'
                'Попробуйте попросить у меня котика позднее')
        bot.send_message(message.chat.id, text)
        bot.send_photo(message.chat.id, requests.get(sad_cat_url).content)
        logger.info('Фото грустного котика отправлено')


def get_new_dog(message: Message) -> str:
    try:
        response = requests.get(DOG_API).json()
        random_image = response[0].get('url')
        return random_image
    except Exception as error:
        logger.warning('API собачек не отвечает!')
        logger.error(f'Ошибка: {error}')
        text = ('К сожалению сервер собачек сейчас недоступен...\n'
                'Попробуйте попросить у меня собачку позднее')
        bot.send_message(message.chat.id, text)
        bot.send_photo(message.chat.id, requests.get(sad_dog_url).content)
        logger.info('Фото грустной собачки отправлено')


def main() -> None:
    try:
        logger.debug('КотоБот запущен')
        server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    except Exception as error:
        logger.critical(f'Ошибка при запуске сервера: {error}')


if __name__ == '__main__':
    main()
