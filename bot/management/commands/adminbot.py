import logging
from django.core.management.base import BaseCommand
from django.conf import settings
import environs
import re
from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
    CallbackQuery
)
from telegram.ext import (
    Updater,
    Filters,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
)

# Ведение журнала логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def step_count():
    step = 1
    while True:
        yield step
        step = step + 1

step_counter = step_count()

class Command(BaseCommand):
    help = 'Телеграм-бот'

    def handle(self, *args, **kwargs):
        env = environs.Env()
        env.read_env()
        tg_token = env('TG_TOKEN')
        updater = Updater(token=tg_token, use_context=True)
        dispatcher = updater.dispatcher

        def start_conversation(update, _):
            query = update.callback_query
            if query:
                query.answer()
            keyboard = [
                [
                    InlineKeyboardButton("Реклама", callback_data='to_ad'),
                    InlineKeyboardButton("Доставки", callback_data="to_delivery"),
                    InlineKeyboardButton("Просрочки", callback_data="to_expired"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            if query:
                query.edit_message_text(
                    text="Выберете интересующий вопрос", reply_markup=reply_markup
                )
            else:
                update.message.reply_text(
                    text="Выберете интресующий вас вопрос", reply_markup=reply_markup
                )

            return 'GREETINGS'


        def get_delivery(update, _):
            query = update.callback_query

            if query.data == 'to_delivery':
                keyboard = [
                    [
                        InlineKeyboardButton("На главный", callback_data="to_start"),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                query.edit_message_text(
                    text="Здесь должен быть текст, содержащий адреса и номера телефонов клиентов",
                    reply_markup=reply_markup,
                )

            query.answer()
            return 'DELIVERY'

        def get_expired(update, _):
            query = update.callback_query

            if query.data == 'to_expired':
                keyboard = [
                    [
                        InlineKeyboardButton("На главный", callback_data="to_start"),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                query.edit_message_text(
                    text="Здесь должен быть текст,\
                     содержащий список просроченных заказов с именами и номерами телефонов владельцев боксов",
                    reply_markup=reply_markup,
                )

            query.answer()
            return 'EXPIRED'


        def show_ad(update, _):
            query = update.callback_query

            keyboard = [
                [
                    InlineKeyboardButton("Добавить", callback_data="add_new_campaign"),
                    InlineKeyboardButton("Статистика", callback_data="to_stat"),
                ],
                [
                    InlineKeyboardButton("На главный", callback_data="to_start"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(
                text="Выберите, что Вы хотите сделать", reply_markup=reply_markup
            )
            query.answer()
            return 'AD'

        def show_stat(update, _):
            query = update.callback_query
            print(query.data)
            campaigns = ['Кампания 1', 'Кампания 2']
            campaigns_keyboard = []
            for i, campaign in enumerate(campaigns):
                callback_data = f"stat_{i}"
                campaigns_keyboard.append([InlineKeyboardButton(campaign, callback_data=callback_data)])

            to_start_keyboard = [
                 [
                    InlineKeyboardButton("На главный", callback_data="to_start"),
                 ]
             ]
            to_stat_keyboard = [
                [
                    InlineKeyboardButton("Кампании", callback_data="to_stat"),
                    InlineKeyboardButton("На главный", callback_data="to_start"),
                ]
            ]
            campaigns_markup = InlineKeyboardMarkup(campaigns_keyboard + to_start_keyboard)
            stat_markup = InlineKeyboardMarkup(to_stat_keyboard)
            query.answer()

            stat_info = ['Статистика по компании 1', 'Статистика по компании 2']

            if query.data == 'to_stat':
                query.edit_message_text(
                    text="Выберите компанию, по которой хотите узнать статистику:", reply_markup=campaigns_markup
                )

            if query.data.startswith('stat_'):
                index = int(query.data.split('_')[1])
                query.edit_message_text(
                    text=stat_info[index], reply_markup=stat_markup
                )

            return 'SHOW_STAT'


        def add_new_campaign(update, _):
            query = update.callback_query
            query.answer()
            keyboard = [
                [
                    InlineKeyboardButton("На главный", callback_data="to_start"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(
                text="В ответном сообщении укажите название новой кампании", reply_markup=reply_markup
            )
            return 'GET_NAME'

        def get_name(update, context):
            text = 'Вы ввели: ' + update.message.text + '\nВведите ссылку, по которой будете просматривать статистику'
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=text)
            return 'GET_URL'

        def get_url(update, context):
            keyboard = [
                [
                    InlineKeyboardButton("Назад", callback_data="to_start"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            text = 'Вы ввели: ' + update.message.text + '\nИнформация о кампании добавлена в БД'
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=text, reply_markup=reply_markup)

            return 'GREETINGS'


        def cancel(update, _):
            user = update.message.from_user
            logger.info("Пользователь %s отменил разговор.", user.first_name)
            update.message.reply_text(
                'До новых встреч',
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END


        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start_conversation)],
            states={
                'GREETINGS': [
                    CallbackQueryHandler(show_ad, pattern='to_ad'),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                    CallbackQueryHandler(get_delivery, pattern='to_delivery'),
                    CallbackQueryHandler(get_expired, pattern='to_expired'),
                ],
                'AD': [
                    CallbackQueryHandler(show_stat, pattern='to_stat'),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                    CallbackQueryHandler(add_new_campaign, pattern='add_new_campaign'),
                ],
                'DELIVERY':[
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                ],
                'EXPIRED': [
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                ],
                'SHOW_STAT': [
                    CallbackQueryHandler(show_stat, pattern='(stat_.*|to_stat)'),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                ],
                'GET_NAME':[
                    MessageHandler(Filters.text, get_name),
                ],
                'GET_URL':[
                    MessageHandler(Filters.text, get_url),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                ],
            },
            fallbacks = [CommandHandler('cancel', cancel)]
        )

        dispatcher.add_handler(conv_handler)

        updater.start_polling()
        updater.idle()
