import logging
import random

from django.core.management.base import BaseCommand
from bot.models import (Client, Order, Storage,
                        DeliveryStatus, Delivery, Box)
from phonenumbers import is_valid_number, parse
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


def calculate_price(weight, size):
    start_price = 750
    weight_cof = None
    size_cof = None
    all_weight_cof = {
        'weight_le_10_cof': 0.7,
        'weight_10to25_cof': 0.9,
        'weight_25to50_cof': 1.1,
        'weight_50to75_cof': 1.3,
        'weight_ge_70_cof': 1.6,
    }
    all_size_cof = {
        'volume_le_1': 0.5,
        'volume_1to3': 0.9,
        'volume_3to7': 1.2,
        'volume_7to10': 1.6,
        'volume_ge_10': 2
    }
    if weight in all_weight_cof:
        weight_cof = all_weight_cof[weight]

    if size in all_size_cof:
        size_cof = all_size_cof[size]

    if weight_cof is None:
        weight_cof = 0.7

    if size_cof is None:
        size_cof = 0.5

    if weight_cof is None and size_cof is None:
        weight_cof = 0.7
        size_cof = 0.5

    month_price = (start_price * weight_cof + start_price * size_cof)
    half_year_price = month_price * 6
    return month_price, half_year_price


def value_from_data(weight, size):
    weight_value = None
    size_value = None
    all_weight = {
        'weight_le_10': "до 10кг",
        'weight_10to25': "10-25кг",
        'weight_25to50': "25-50кг",
        'weight_50to75': "50-75кг",
        'weight_ge_70': "75кг+",
    }
    all_size = {
        'volume_le_1': "менее 1 куб.м",
        'volume_1to3': "1 - 3 куб.м",
        'volume_3to7': "3 - 7 куб.м",
        'volume_7to10': "7 - 10 куб.м",
        'volume_ge_10': "более 10 куб.м"
    }
    if weight in all_weight:
        weight_value = all_weight[weight]

    if size in all_size:
        size_value = all_size[size]

    if not weight in all_weight:
        weight_value = "Необходимо замерить"

    if not size in all_size:
        size_value = "Необходимо замерить"

    return weight_value, size_value


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
                    text="Выберете интересующий вас вопрос", reply_markup=reply_markup
                )

            return 'GREETINGS'

        def faq(update, _):
            query = update.callback_query

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

        def order_box(update, context):
            query = update.callback_query

            if query.data == 'to_box_order':
                storage = Storage.objects.all()[0]
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
                    text=f"Наш склад {storage.name} находится по адресу:\n" +
                         f"{storage.address}\n" +
                         'Для заказа бокса,пожалуйста, выберите, как удобнее передать вещи:',
                    reply_markup=reply_markup
                )
            if query.data == 'Привезу_сам' or query.data == 'Заберите_бесплатно':
                type_delivery = query.data
                context.user_data['type_delivery'] = type_delivery
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
                choose_weight = query.data
                context.user_data['choose_weight'] = choose_weight
                keyboard = [
                    [
                        InlineKeyboardButton("до 10кг", callback_data="weight_le_10"),
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

            if query.data == "weight_le_10" or "weight_10to25" or 'weight_25to50' or \
                    'weight_50to75' or "weight_ge_70" in query.data:
                weight = query.data
                context.user_data['weight'] = weight

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
                choose_volume = query.data
                context.user_data['choose_volume'] = choose_volume
                keyboard = [
                    [
                        InlineKeyboardButton("менее 1 куб.м", callback_data="volume_le_1"),
                        InlineKeyboardButton("1 - 3 куб.м", callback_data="volume_1to3"),
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

            if query.data == "volume_le_1" or "volume_1to3" or 'volume_3to7' or \
                    'volume_7to10' or "volume_ge_10" in query.data:
                size = query.data
                context.user_data['size'] = size

            if re.match("^volume_", query.data) or query.data == 'no_volume_info' or query.data == 'no_weight_info':
                keyboard = [
                    [
                        InlineKeyboardButton("Согласен на обработку персональных данных",
                                             callback_data="personal_data_processing"),
                    ],
                    [
                        InlineKeyboardButton("На главный", callback_data="to_start"),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                if re.match("^volume_", query.data):
                    size = context.user_data.get('size')
                    weight = context.user_data.get('weight')
                    month_price, half_year_price = calculate_price(weight, size)
                    text = "Спасибо за оформление заказа.\n" \
                           "Примерная стоимость на 1 календарный месяц " \
                           f"составляет {month_price} RUB.\n" \
                           f"Примерная стоимость на пол года {half_year_price} RUB.\n" \
                           "Чтобы продолжить оформление в соответствии с законодательством " \
                           "нам нужно Ваше согласие на обработку персональный данных"
                    query.edit_message_text(
                        text=text, reply_markup=reply_markup
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

        def process_personal_data(update, context):
            query = update.callback_query
            personal_data_consent_date = True
            context.user_data['personal_data_consent_date'] = personal_data_consent_date
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
            chat_id = update.message.chat_id
            nickname = update.message.from_user.username
            name = update.message.text
            context.user_data['chat_id'] = chat_id
            context.user_data['nickname'] = nickname
            context.user_data['name'] = name

            text = '✅ Ув. {}\n\n<b>Введите ваш адрес</b> '.format(update.message.text)
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=text)
            return 'GET_ADDRESS'

        def get_address(update, context):
            address = update.message.text
            context.user_data['address'] = address

            text = '<b>Введите номер телефона:</b>'
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=text)
            return 'GET_PHONE'

        def get_phone(update, context):
            phone_number = update.message.text
            if is_valid_number(parse(phone_number, 'RU')):
                context.user_data['phone_number'] = phone_number
                text = '<b>Введите email</b>'
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text=text)
                return 'GET_EMAIL'
            else:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text='Введите корректный номер')
                return 'GET_PHONE'

        def get_email(update, context):
            email = update.message.text
            context.user_data['email'] = email
            text = 'ECHO: ' + update.message.text + '<b> Введите список вещей в одном сообщении</b>'
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=text)
            return 'GET_ITEM_LIST'

        def get_item_list(update, context):
            things = update.message.text
            context.user_data['things'] = things
            text = 'ECHO: ' + update.message.text + ' Назовите заказ \n' \
                                                    'Например, зимние куртки ' \
                                                    'или Спорт инвентарь'
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=text)
            return 'GET_ORDER_NAME'

        def get_order_name(update, context):
            chat_id = update.effective_chat.id
            title = update.message.text
            size = context.user_data.get('size')
            weight = context.user_data.get('weight')
            weight_value, size_value = value_from_data(weight, size)
            type_delivery = context.user_data.get('type_delivery')
            nickname = context.user_data.get('nickname')
            name = context.user_data.get('name')
            phone_number = context.user_data.get('phone_number')
            address = context.user_data.get('address')
            email = context.user_data.get('email')
            things = context.user_data.get('things')

            all_box = Box.objects.all()
            random_box = random.choice(all_box)
            print('random_box = ', random_box)
            profile, _ = Client.objects.get_or_create(chat_id=chat_id,
                                                      defaults={
                                                          'nickname': nickname,
                                                          'name': name,
                                                          'address': address,
                                                          'email': email,
                                                          'tel_number': phone_number,
                                                          'personal_data_consent': True
                                                      })
            order = Order.objects.create(
                client=profile,
                weight=weight_value,
                size=size_value,
                things=things,
                title=title,
                delivery_type=type_delivery,
                box=random_box,
            )
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

                'SHOW_INFO': [
                    CallbackQueryHandler(faq, pattern='(FAQ_.*|address|price|schedule|contacts)'),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                ],
                'ORDER_BOX': [
                    CallbackQueryHandler(order_box, pattern='(Привезу_сам|Заберите_бесплатно|.*weight.*|.*volume.*)'),
                    CallbackQueryHandler(process_personal_data, pattern='personal_data_processing'),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                ],
                'PERSONAL_PROCCESSING': [
                    CallbackQueryHandler(process_personal_data, pattern='personal_data_processing'),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                    MessageHandler(Filters.text, get_name),
                ],
                'GET_ADDRESS': [
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                    MessageHandler(Filters.text, get_address),
                ],
                'GET_PHONE': [
                    MessageHandler(Filters.text, get_phone),
                ],
                'GET_EMAIL': [
                    MessageHandler(Filters.text, get_email),
                ],
                'GET_ITEM_LIST': [
                    MessageHandler(Filters.text, get_item_list),
                ],
                'GET_ORDER_NAME': [
                    MessageHandler(Filters.text, get_order_name),
                ],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )

        dispatcher.add_handler(conv_handler)

        updater.start_polling()
        updater.idle()
