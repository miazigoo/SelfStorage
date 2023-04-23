import datetime
import logging
import random

import qrcode
from os import remove
from bot.faq_answers import FAQ_ANSWERS
from django.core.management.base import BaseCommand
from django.core.validators import validate_email
from phonenumbers import is_valid_number, parse
from SelfStorage import settings
import re
from bot.models import (Client, Order, Storage, DeliveryType,
                        DeliveryStatus, Delivery, Box)
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove, ParseMode,
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


def send_qr(update, updater):
    chat_id = update.callback_query.message.chat.id
    img_name = f"tmp_qr_{chat_id}.png"
    img = qrcode.make(chat_id)
    img.save(img_name)
    with open(img_name, 'rb') as qr:
        updater.bot.send_photo(chat_id=chat_id, photo=qr)
    remove(img_name)


with open('bot/hello.txt', encoding="utf-8", mode='r') as file:
    start_text = file.read()


def calculate_price(weight, size):
    start_price = 750
    all_weight_cof = {
        'weight_le_10': 0.7,
        'weight_10to25': 0.9,
        'weight_25to50': 1.1,
        'weight_50to75': 1.3,
        'weight_ge_70': 1.6,
    }
    all_size_cof = {
        'volume_le_1': 0.5,
        'volume_1to3': 0.9,
        'volume_3to7': 1.2,
        'volume_7to10': 1.6,
        'volume_ge_10': 2,
    }
    if weight in all_weight_cof:
        weight_cof = all_weight_cof[weight]
    else:
        weight_cof = 0.7

    if size in all_size_cof:
        size_cof = all_size_cof[size]
    else:
        size_cof = 0.5

    month_price = (start_price * weight_cof + start_price * size_cof)
    half_year_price = month_price * 6
    return month_price, half_year_price


def value_from_data(weight, size):
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
        'volume_ge_10': "более 10 куб.м",
    }
    if weight in all_weight:
        weight_value = all_weight[weight]
    else:
        weight_value = "Необходимо замерить"

    if size in all_size:
        size_value = all_size[size]
    else:
        size_value = "Необходимо замерить"

    return weight_value, size_value


class Command(BaseCommand):
    help = 'Телеграм-бот'

    def handle(self, *args, **kwargs):
        tg_token = settings.tg_token
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
                    InlineKeyboardButton("Мои Боксы", callback_data="to_my_orders"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            if query:
                query.edit_message_text(
                    text=f"{start_text}\nВыберете интересующий вопрос", reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML
                )
            else:
                update.message.reply_text(
                    text=f"{start_text}\nВыберете интересующий вас вопрос", reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML
                )

            return 'GREETINGS'

        def faq(update, _):
            query = update.callback_query

            keyboard = [
                [
                    InlineKeyboardButton("Что можно хранить", callback_data='FAQ_что_хранить'),
                    InlineKeyboardButton("Нельзя хранить", callback_data='FAQ_нельзя_хранить'),
                    InlineKeyboardButton("Как храним", callback_data="FAQ_как_храним"),
                ],
                [
                    InlineKeyboardButton("Адрес", callback_data='FAQ_address'),
                    InlineKeyboardButton("Цены", callback_data='FAQ_price'),
                    InlineKeyboardButton("Режим Работы", callback_data="FAQ_schedule"),
                ],
                [
                    InlineKeyboardButton("Как оформить хранение", callback_data='FAQ_оформить_хранение'),
                    InlineKeyboardButton("Как забрать вещи", callback_data='FAQ_забрать_вещи'),
                ],
                [
                    InlineKeyboardButton("Контакты", callback_data='FAQ_contacts'),
                    InlineKeyboardButton("На главный", callback_data="to_start"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.answer()
            if query.data == 'to_FAQ':
                query.edit_message_text(
                    text="Выберете интересующий вопрос", reply_markup=reply_markup
                )
            else:
                query.edit_message_text(
                    text=FAQ_ANSWERS[query.data], reply_markup=reply_markup
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

            if re.match(r'^weight_.*', query.data):
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

            if re.match(r'^volume_.*', query.data):
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

            keyboard = [
                [
                    InlineKeyboardButton("Назад", callback_data="to_start"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(
                text="✅ Ув. {}\n\n<b>Введите ваш адрес</b> ", reply_markup=reply_markup
            )

            return 'GET_ADDRESS'

        def get_address(update, context):
            address = update.message.text
            context.user_data['address'] = address

            keyboard = [
                [
                    InlineKeyboardButton("Назад", callback_data="to_start"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(
                text='✅ <b>Введите номер телефона:</b>', reply_markup=reply_markup
            )

            return 'GET_PHONE'

        def get_phone(update, context):
            phone_number = update.message.text
            if is_valid_number(parse(phone_number, 'RU')):
                context.user_data['phone_number'] = phone_number
                keyboard = [
                    [
                        InlineKeyboardButton("Назад", callback_data="to_start"),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text(
                    text='✅ <b>Введите email:</b>', reply_markup=reply_markup
                )

                return 'GET_EMAIL'
            else:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text='Введите корректный номер')
                return 'GET_PHONE'

        def get_email(update, context):
            email = update.message.text
            if re.match(r'\w[\w\.-]*@\w[\w\.-]+\.\w+', email):
                context.user_data['email'] = email

                keyboard = [
                    [
                        InlineKeyboardButton("Назад", callback_data="to_start"),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text(
                    text='✅ <b> Введите список вещей в одном сообщении</b>', reply_markup=reply_markup
                )

                return 'GET_ITEM_LIST'
            else:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text='Введите корректный email')
                return 'GET_EMAIL'

        def get_item_list(update, context):
            things = update.message.text
            context.user_data['things'] = things

            keyboard = [
                [
                    InlineKeyboardButton("Назад", callback_data="to_start"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(
                text='✅ Назовите заказ. апример, зимние куртки или Спорт инвентарь', reply_markup=reply_markup
            )

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
                box=random_box,
            )
            delivery_type = DeliveryType.objects.get_or_create(name=type_delivery)

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

        def show_my_orders(update, context):
            query = update.callback_query
            chat_id = update.effective_chat.id
            orders = Order.objects.filter(end_storage_date__isnull=True, client__chat_id=chat_id)
            query.answer()

            if query.data == 'to_my_orders':
                if not orders:
                    keyboard = [
                        [
                            InlineKeyboardButton("Заказать Бокс", callback_data="to_box_order"),
                            InlineKeyboardButton("На главный", callback_data="to_start"),
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    query.edit_message_text(
                        text="У нас еще нет Ваших вещей на хранении", reply_markup=reply_markup
                    )
                else:
                    orders_keyboard = []
                    for order in orders:
                        callback_data = f"order_{order.pk}"
                        orders_keyboard.append([InlineKeyboardButton(order.title, callback_data=callback_data)])

                    to_start_keyboard = [
                        [
                            InlineKeyboardButton("На главный", callback_data="to_start"),
                        ]
                    ]
                    orders_markup = InlineKeyboardMarkup(orders_keyboard + to_start_keyboard)
                    query.edit_message_text(
                        text=f"У вас есть {len(orders)} боксов. Выберите нужный", reply_markup=orders_markup
                    )

            if query.data.startswith('order_') or query.data == 'FAQ_forget':
                order_keyboard = [
                    [
                        InlineKeyboardButton("Забрать вещи", callback_data="take_things"),
                        InlineKeyboardButton("Список вещей", callback_data="list_things"),
                    ],
                    [
                        InlineKeyboardButton("Забыл забрать! Что делать?", callback_data="FAQ_forget"),
                    ],
                ]
                to_orders_keyboard = [
                    [
                        InlineKeyboardButton("Заказы", callback_data="to_my_orders"),
                        InlineKeyboardButton("На главный", callback_data="to_start"),
                    ]
                ]
                order_markup = InlineKeyboardMarkup(order_keyboard + to_orders_keyboard)
                if query.data.startswith('order_'):
                    order_pk = int(query.data.split('_')[1])
                    context.user_data['order_pk'] = order_pk
                    query.edit_message_text(
                        text="Что Вы хотите сделать?", reply_markup=order_markup
                    )
                else:
                    query.edit_message_text(
                        text=FAQ_ANSWERS[query.data], reply_markup=order_markup
                    )
            if query.data == "list_things":
                order = orders.get(id=context.user_data['order_pk'])
                keyboard = [
                    [
                        InlineKeyboardButton("Заказы", callback_data="to_my_orders"),
                        InlineKeyboardButton("На главный", callback_data="to_start"),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                query.edit_message_text(
                    text=f"Ваш список вещей: {order.things}", reply_markup=reply_markup
                )
            if query.data == 'take_things':
                keyboard = [
                    [
                        InlineKeyboardButton("Доставка на дом", callback_data="to_delivery"),
                        InlineKeyboardButton("Заберу сам", callback_data="to_self_delivery"),
                    ],
                    [
                        InlineKeyboardButton("Заказы", callback_data="to_my_orders"),
                        InlineKeyboardButton("На главный", callback_data="to_start"),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                query.edit_message_text(
                    text="Пожалуйста, выберите, как вы хотите забрать вещи:", reply_markup=reply_markup
                )
            return 'SHOW_ORDERS'

        def process_delivery(update, context):
            query = update.callback_query
            chat_id = update.effective_chat.id
            close_time = datetime.date.today()
            client = Client.objects.filter(chat_id=chat_id)[0]
            order_pk = context.user_data['order_pk']
            order = Order.objects.get(pk=order_pk)
            if query:
                query.answer()

            if re.match(r'.*_delivery$', query.data):
                context.user_data['self_delivery'] = False
                if query.data == "to_self_delivery":
                    context.user_data['self_delivery'] = True
                keyboard = [
                    [
                        InlineKeyboardButton("Насовсем", callback_data="Насовсем"),
                        InlineKeyboardButton("Верну Обратно", callback_data="Верну"),
                    ],
                    [
                        InlineKeyboardButton("Заказы", callback_data="to_my_orders"),
                        InlineKeyboardButton("На главный", callback_data="to_start"),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                query.edit_message_text(
                    text="Вы хотите забрать вещи насовсем?", reply_markup=reply_markup
                )

            if context.user_data['self_delivery'] and (query.data == "Насовсем" or query.data == "Верну"):
                storage = Storage.objects.all()[0]
                send_qr(update, updater)
                keyboard = [
                    [
                        InlineKeyboardButton("На главный", callback_data="to_start"),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                context.bot.send_message(
                    text=f'Вы можете забрать Ваши вещи в любое удобное для Вас время по адреcу: {storage.address}. ' \
                         'Склад работает круглосуточно. Прилагаемый QR-код является ключом для Вашего бокса. ' \
                         'Если хотел вернуть обратно: Вы можете в любой момент вернуть вещи обратно на хранение. ' \
                         'Для этого Вы можете либо самостоятельно привезти их нам, либо заказать доставку.',
                    chat_id=update.effective_chat.id,
                    reply_markup=reply_markup
                )

            if not context.user_data['self_delivery'] and (query.data == "Насовсем" or query.data == "Верну"):
                keyboard = [
                    [
                        InlineKeyboardButton("Подтвердить", callback_data="accept"),
                        InlineKeyboardButton("Заказы", callback_data="to_my_orders"),
                        InlineKeyboardButton("На главный", callback_data="to_start"),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                query.edit_message_text(
                    text=f"Вы хотите, чтобы мы привезли Вам вещи по адресу {client.address} за 12 рублей/километр?",
                    reply_markup=reply_markup
                )
            if query.data == "Насовсем":
                order.end_storage_date = close_time
                order.save()
            if query.data == "accept":
                keyboard = [
                    [
                        InlineKeyboardButton("На главный", callback_data="to_start"),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                query.edit_message_text(
                    text=f'Ваш заказ №{order_pk} на доставку успешно сформирован! ' \
                         'В ближайшее время с Вами свяжется наш специалист для уточнения времени доставки.',
                    reply_markup=reply_markup
                )

            return 'DELIVERY'

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
                    CallbackQueryHandler(show_my_orders, pattern='to_my_orders'),
                ],

                'SHOW_INFO': [
                    CallbackQueryHandler(faq, pattern='(FAQ_.*)'),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                ],
                'SHOW_ORDERS': [
                    CallbackQueryHandler(show_my_orders, pattern='to_my_orders|order_.*|FAQ_forget|.*_things'),
                    CallbackQueryHandler(order_box, pattern='to_box_order'),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                    CallbackQueryHandler(process_delivery, pattern='.*_delivery')
                ],
                'DELIVERY': [
                    CallbackQueryHandler(process_delivery, pattern='(Насовсем|Верну|accept)'),
                    CallbackQueryHandler(show_my_orders, pattern='to_my_orders'),
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
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                    MessageHandler(Filters.text, get_phone),
                ],
                'GET_EMAIL': [
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                    MessageHandler(Filters.text, get_email),
                ],
                'GET_ITEM_LIST': [
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                    MessageHandler(Filters.text, get_item_list),
                ],
                'GET_ORDER_NAME': [
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                    MessageHandler(Filters.text, get_order_name),
                ],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )

        dispatcher.add_handler(conv_handler)
        start_handler = CommandHandler('start', start_conversation)
        dispatcher.add_handler(start_handler)

        updater.start_polling()
        updater.idle()
