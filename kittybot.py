import logging
import os
import random
import sys
import time
from logging import StreamHandler
from typing import Tuple

import requests
import telebot
from dotenv import load_dotenv
from flask import Flask, request
from telebot import types
from telegram import Message

from congratulation import correct, image_urls, incorrect

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = StreamHandler(sys.stderr)
logger.addHandler(handler)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
APP_URL = f'https://kot0bot.herokuapp.com/{TELEGRAM_TOKEN}'
CAT_API = 'https://api.thecatapi.com/v1/images/search'
DOG_API = 'https://api.thedogapi.com/v1/images/search'
SAD_CAT_URL = ('https://avatars.yandex.net/get-music-user-playlist/34120/'
               '546136583.1000.75797/m1000x1000?1546676930515&webp=false')
SAD_DOG_URL = ('https://avatars.mds.yandex.net/get-zen_doc/1898210/pub_5dcc'
               'fee9d2bc1447e8b05424_5dccff4bcd7152643c8dc951/scale_1200')
# DARYA_ID = 987237365
DARYA_ID = 632658705

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


@bot.message_handler(commands=['valentine'])
def congratulations(message: Message) -> None:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    new_image = types.InlineKeyboardButton('😍 Хочу новую открытку! 😍')
    markup.add(new_image)
    congratulation = ('Прими от меня и моего создателя '
                      '(по совместительству твоего мужа) '
                      'поздравления с Днем Святого Валентина '
                      'и конечно же с вашей годовщиной! ❤')
    try:
        bot.reply_to(
            message,
            'Выполняю секретный код!'
        )
        time.sleep(5)
        bot.send_message(DARYA_ID, 'Дарюша, доброе утро! 😍')
        time.sleep(3)
        bot.send_message(DARYA_ID, 'Это твой Котобот 😊')
        time.sleep(6)

        bot.send_message(DARYA_ID, 'Стоп, ты не Дарюша!')
        time.sleep(3)
        bot.send_message(DARYA_ID, ('Гнусный пидор!!!\n'
                                    'Хотел наебать Котобота??!?!?!?'))
        time.sleep(2)
        bot.send_message(DARYA_ID, 'Лан, хуй с тобой!')
        time.sleep(2)

        bot.send_message(DARYA_ID, congratulation)
        time.sleep(6)
        bot.send_message(DARYA_ID, '❤ Эти открыточки для Тебя! ❤')
        time.sleep(4)
        bot.send_photo(DARYA_ID, image_urls[0], reply_markup=markup)
        logger.info('Сообщения и открытка отправлены')
    except Exception as error:
        logger.error(f'Ошибка отправки сообщений: {error}')


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
        elif message.text == '😍 Хочу новую открытку! 😍':
            text = ['Пожалуйста!', 'Держи!', 'Это можно!',
                    'Запросто!', 'Конечно!', 'Отправляю!']
            sorry = ['Ой, сорян...', 'Упс...', 'Извините...',
                     'Прошу прощения...']
            image = random.choice(image_urls)
            if image != incorrect:
                bot.send_message(DARYA_ID, random.choice(text))
                time.sleep(2)
                bot.send_photo(DARYA_ID, image)
            else:
                bot.send_message(DARYA_ID, random.choice(text))
                time.sleep(2)
                bot.send_photo(DARYA_ID, image)
                time.sleep(2)
                bot.send_message(DARYA_ID, random.choice(sorry))
                time.sleep(2)
                bot.send_photo(DARYA_ID, correct)
            logger.info('Открытка отправлена')
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
        return response[0].get('url')
    except Exception as error:
        logger.warning('API котиков не отвечает!')
        logger.error(f'Ошибка: {error}')
        text = ('К сожалению сервер котиков сейчас недоступен...\n'
                'Попробуйте попросить у меня котика позднее')
        bot.send_message(message.chat.id, text)
        bot.send_photo(message.chat.id, requests.get(SAD_CAT_URL).content)
        logger.info('Фото грустного котика отправлено')


def get_new_dog(message: Message) -> str:
    try:
        response = requests.get(DOG_API).json()
        return response[0].get('url')
    except Exception as error:
        logger.warning('API собачек не отвечает!')
        logger.error(f'Ошибка: {error}')
        text = ('К сожалению сервер собачек сейчас недоступен...\n'
                'Попробуйте попросить у меня собачку позднее')
        bot.send_message(message.chat.id, text)
        bot.send_photo(message.chat.id, requests.get(SAD_DOG_URL).content)
        logger.info('Фото грустной собачки отправлено')


def main() -> None:
    try:
        logger.debug('КотоБот запущен')
        server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    except Exception as error:
        logger.critical(f'Ошибка при запуске сервера: {error}')


if __name__ == '__main__':
    main()
