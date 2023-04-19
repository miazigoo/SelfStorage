import logging
import os

from dotenv import load_dotenv, find_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import MessageHandler, Filters, CallbackQueryHandler
from telegram.ext import Updater, CallbackContext, CommandHandler

load_dotenv(find_dotenv())

token = os.environ['TG_TOKEN']

updater = Updater(token=token)

dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


def send_message(file, update, context):
    with open(file) as file:
        text = file.readlines()
        text = ' '.join(text)
    if len(text) > 4096:
        for x in range(0, len(text), 4096):
            context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode='HTML')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode='HTML')


def start(update: Update, context: CallbackContext):
    rules = InlineKeyboardButton('Правила', callback_data='rules')
    user_registration = InlineKeyboardButton('Регистрация', callback_data='user_registration')
    rent_box = InlineKeyboardButton('Арендовать бокс', callback_data='rent_box')
    row1 = [rules, user_registration]
    row2 = [rent_box]
    reply_markup = InlineKeyboardMarkup([row1, row2], resize_keyboard=True, one_time_keyboard=True)
    send_message('hello.txt', update, context)
    update.message.reply_text('Главное меню сервиса SelfStorage:', reply_markup=reply_markup)


def button_callback(update, context):
    callback_data = update.callback_query.data
    if callback_data == 'rules':
        update.callback_query.message.reply_text('Здесь должны быть отправлены правила хранения')
    elif callback_data == 'user_registration':
        update.callback_query.message.reply_text('Эта кнопка запускает процедуру регистрации пользователя')
    elif callback_data == 'rent_box':
        update.callback_query.message.reply_text('Эта кнопка запускает процедуру аренды бокса')


start_handler = CommandHandler('start', start)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(CallbackQueryHandler(button_callback))

updater.start_polling()
