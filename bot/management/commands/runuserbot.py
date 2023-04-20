import logging
from django.core.management.base import BaseCommand
from phonenumbers import is_valid_number, parse
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
                    InlineKeyboardButton("FAQ", callback_data='to_FAQ'),
                    InlineKeyboardButton("Заказать Бокс", callback_data="to_box_order"),
                    InlineKeyboardButton("Мои Боксы", callback_data="Мои Боксы"),
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

        def faq(update, _):
            query = update.callback_query
            print(query.data)

            keyboard = [
                [
                    InlineKeyboardButton("Можно хранить", callback_data='FAQ_1'),
                    InlineKeyboardButton("Нельзя хранить", callback_data='FAQ_2'),
                    InlineKeyboardButton("Как храним", callback_data="FAQ_3"),
                ],
                [
                    InlineKeyboardButton("Адрес", callback_data='address'),
                    InlineKeyboardButton("Цены", callback_data='price'),
                    InlineKeyboardButton("Режим Работы", callback_data="schedule"),
                ],
                [
                    InlineKeyboardButton("Как оформить хранение", callback_data='FAQ_4'),
                    InlineKeyboardButton("Как забрать вещи", callback_data='FAQ_5'),
                ],
                [
                    InlineKeyboardButton("Контакты", callback_data='contacts'),
                    InlineKeyboardButton("На главный", callback_data="to_start"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            query.answer()

            if query.data == 'to_FAQ':
                query.edit_message_text(
                    text="Выберете интересующий вопрос", reply_markup=reply_markup
                )

            if query.data == 'FAQ_1':
                query.edit_message_text(
                    text=f'Выводим  ответ на  {query.data}', reply_markup=reply_markup
                )
            if query.data == 'FAQ_2':
                query.edit_message_text(
                    text=f'Выводим  ответ на  {query.data}', reply_markup=reply_markup
                )
            if query.data == 'FAQ_3':
                query.edit_message_text(
                    text=f'Выводим  ответ на  {query.data}', reply_markup=reply_markup
                )
            if query.data == 'FAQ_4':
                query.edit_message_text(
                    text=f'Выводим  ответ на  {query.data}', reply_markup=reply_markup
                )
            if query.data == 'FAQ_5':
                query.edit_message_text(
                    text=f'Выводим  ответ на  {query.data}', reply_markup=reply_markup
                )
            if query.data == 'address':
                query.edit_message_text(
                    text=f'Выводим  ответ на  {query.data}', reply_markup=reply_markup
                )
            if query.data == 'price':
                query.edit_message_text(
                    text=f'Выводим  ответ на  {query.data}', reply_markup=reply_markup
                )
            if query.data == 'schedule':
                query.edit_message_text(
                    text=f'Выводим  ответ на  {query.data}', reply_markup=reply_markup
                )
            if query.data == 'contacts':
                query.edit_message_text(
                    text=f'Выводим  ответ на  {query.data}', reply_markup=reply_markup
                )
            return 'SHOW_INFO'

        def order_box(update, _):
            query = update.callback_query

            if query.data == 'to_box_order':
                keyboard = [
                    [
                        InlineKeyboardButton("Привезу сам", callback_data="Привезу_сам"),
                        InlineKeyboardButton("Заберите бесплатно", callback_data="Заберите_бесплатно"),
                    ],
                    [
                        InlineKeyboardButton("На главный", callback_data="to_start"),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                query.edit_message_text(
                    text="Для заказа бокса,пожалуйста, выберите, как удобнее передать вещи:", reply_markup=reply_markup
                )
            if query.data == 'Привезу_сам' or query.data == 'Заберите_бесплатно':
                keyboard = [
                    [
                        InlineKeyboardButton("Укажите вес", callback_data="choose_weight"),
                        InlineKeyboardButton("Не знаю", callback_data="no_weight_info"),
                    ],
                    [
                        InlineKeyboardButton("На главный", callback_data="to_start"),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                query.edit_message_text(
                    text="Знаете ли Вы вес своих вещей?", reply_markup=reply_markup
                )
            if query.data == 'choose_weight':
                keyboard = [
                    [
                        InlineKeyboardButton("до 10 кг", callback_data="weight_le_10"),
                        InlineKeyboardButton("10-25кг", callback_data="weight_10to25"),
                        InlineKeyboardButton("25-50кг", callback_data="weight_25to50"),
                    ],
                    [
                        InlineKeyboardButton("50-75кг", callback_data="weight_50to75"),
                        InlineKeyboardButton("75кг+", callback_data="weight_ge_70"),
                        InlineKeyboardButton("На главный", callback_data="to_start"),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                query.edit_message_text(
                    text="Выберите вес", reply_markup=reply_markup
                )
            if query.data == 'no_weight_info' or 'weight_' in query.data:
                keyboard = [
                    [
                        InlineKeyboardButton("Укажите объем", callback_data="choose_volume"),
                        InlineKeyboardButton("Не знаю", callback_data="no_volume_info"),
                    ],
                    [
                        InlineKeyboardButton("На главный", callback_data="to_start"),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                query.edit_message_text(
                    text="Знаете ли объем ваших вещей", reply_markup=reply_markup
                )
            if query.data == 'choose_volume':
                keyboard = [
                    [
                        InlineKeyboardButton("менее 1 куб.м ", callback_data="volume_le_1"),
                        InlineKeyboardButton("1 - 3 куб.м ", callback_data="volume_1to3"),
                        InlineKeyboardButton("3 - 7 куб.м", callback_data="volume_3to7"),
                    ],
                    [
                        InlineKeyboardButton("7 - 10 куб.м", callback_data="volume_7to10"),
                        InlineKeyboardButton("более 10 куб.м", callback_data="volume_ge_10"),
                        InlineKeyboardButton("На главный", callback_data="to_start"),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                query.edit_message_text(
                    text="Выберите объем", reply_markup=reply_markup
                )
            if re.match("^volume_", query.data) or query.data == 'no_volume_info' or query.data == 'no_weight_info':
                keyboard = [
                    [
                        InlineKeyboardButton("Согласен на обработку персональных данных", callback_data="personal_data_processing"),
                    ],
                    [
                        InlineKeyboardButton("На главный", callback_data="to_start"),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                if re.match("^volume_", query.data):
                    query.edit_message_text(
                        text='''Спасибо за оформление заказа. Примерная стоимость составляет ХХ.
                              Чтобы продолжить оформление в соответствии с законодательством 
                             нам нужно Ваше согласие на обработку персональный данных ''', reply_markup=reply_markup
                    )
                else:
                    query.edit_message_text(
                        text='''Спасибо за оформление заказа.
                                Чтобы продолжить оформление в соответствии с законодательством 
                                нам нужно Ваше согласие на обработку персональный данных ''',
                        reply_markup=reply_markup
                    )

            query.answer()
            return 'ORDER_BOX'

        def process_personal_data(update, _):
            query = update.callback_query
            query.answer()
            keyboard = [
                [
                    InlineKeyboardButton("Назад", callback_data="to_start"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(
                text="В ответном сообщении укажите Ваш имя.", reply_markup=reply_markup
            )
            return 'PERSONAL_PROCCESSING'

        def get_name(update, context):
            text = 'Вы ввели: ' + update.message.text + 'Введите адрес'
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=text)
            return 'GET_ADDRESS'

        def get_address(update, context):
            text = 'ECHO: ' + update.message.text + 'Введите телефон'
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=text)
            return 'GET_PHONE'

        def get_phone(update, context):
            phonenumber = update.message.text
            if is_valid_number(parse(phonenumber, 'RU')):
                text = 'ECHO: ' + update.message.text + 'Введите email'
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text=text)
                return 'GET_EMAIL'
            else:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text='Введите коректный номер')
                return 'GET_PHONE'


        def get_email(update, context):
            text = 'ECHO: ' + update.message.text + 'Введите список вещей'
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=text)
            return 'GET_ITEM_LIST'

        def get_item_list(update, context):
            text = 'ECHO: ' + update.message.text + 'Назовите заказ'
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=text)
            return 'GET_ORDER_NAME'

        def get_order_name(update, _):
            keyboard = [
                [
                    InlineKeyboardButton("Назад", callback_data="to_start"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(
                text="Ваш заказ успешно создан", reply_markup=reply_markup
            )
            return 'GREETINGS'

        def update_form(update, _):
            query = update.callback_query
            query.answer()
            keyboard = [
                [
                    InlineKeyboardButton("Изменить", callback_data="update_field"),
                    InlineKeyboardButton("Назад", callback_data="to_start"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(
                text=f"Обновить {query.data}", reply_markup=reply_markup
            )
            return 'ORDER_BOX'

        # def send_field_info(update, _):
        #     query = update.callback_query
        #     query.edit_message_text(
        #         f'Обновялем {query.data} Введите новое значение'
        #     )
        #     return 'UPDATE'
        #
        # def update_field(update, _):
        #     user = update.message.from_user
        #     chat_instance = update.message.chat.id
        #     logger.info("Пользователь %s рассказал: %s", user.first_name, update.message.text)
        #     text = update.message.text
        #     update.message.reply_text(f'Спасибо! Вы ввели {text}')
        #     print(update)
        #
        #     return 'BACK_TO_GREETINGS'
        #
        # def echo(update, context):
        #     # добавим в начало полученного сообщения строку 'ECHO: '
        #     text = 'ECHO: ' + update.message.text
        #     context.bot.send_message(chat_id=update.effective_chat.id,
        #                              text=text)
        #     print(update)


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
                    CallbackQueryHandler(faq, pattern='to_FAQ'),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                    CallbackQueryHandler(order_box, pattern='to_box_order'),
                    CallbackQueryHandler(update_form, pattern='(update_name|update_phone|update_email|update_address)'),
                ],

                'SHOW_INFO':[
                    CallbackQueryHandler(faq, pattern='(FAQ_.*|address|price|schedule|contacts)'),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                ],
                'ORDER_BOX':[
                    CallbackQueryHandler(order_box, pattern='(Привезу_сам|Заберите_бесплатно|.*weight.*|.*volume.*)'),
                    CallbackQueryHandler(process_personal_data, pattern='personal_data_processing'),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                ],
                'PERSONAL_PROCCESSING':[
                    CallbackQueryHandler(process_personal_data, pattern='personal_data_processing'),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                    MessageHandler(Filters.text, get_name),
                ],
                'GET_ADDRESS':[
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                    MessageHandler(Filters.text, get_address),
                ],
                'GET_PHONE':[
                    MessageHandler(Filters.text, get_phone),
                ],
                'GET_EMAIL':[
                    MessageHandler(Filters.text, get_email),
                ],
                'GET_ITEM_LIST': [
                    MessageHandler(Filters.text, get_item_list),
                ],
                'GET_ORDER_NAME': [
                    MessageHandler(Filters.text, get_order_name),
                ],
            },
            fallbacks = [CommandHandler('cancel', cancel)]
        )

        dispatcher.add_handler(conv_handler)

        updater.start_polling()
        updater.idle()
