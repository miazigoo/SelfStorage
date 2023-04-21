import logging

from django.core.management import BaseCommand
from environs import Env
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from telegram.ext import Updater, CallbackContext, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, \
    ConversationHandler

from bot.models import Client

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

MENU, CHOOSING, TYPING_REPLY, TYPING_CHOICE, \
FULL_NAME, PHONE_NUBER, EMAIL, PERSONAL_DATA_CONSENT = range(8)

reply_keyboard = [
    ["Меню", "Favourite colour"],
    ["Number of siblings", "Something else..."],
    ["Done"],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def log_errors(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            error_message = f'Произошла ошибка: {e}'
            print(error_message)
            raise e

    return inner


class Command(BaseCommand):
    help = 'Телеграм-бот'

    def handle(self, *args, **options):
        env = Env()
        env.read_env()

        tg_token = env.str('TG_TOKEN')
        updater = Updater(token=tg_token)

        dispatcher = updater.dispatcher
        profile_order = {}

        def start_conversation(update, _):
            query = update.callback_query
            if query:
                query.answer()
            keyboard = [
                [
                    InlineKeyboardButton("Профиль", callback_data='to_profile'),
                    InlineKeyboardButton("FAQ", callback_data='to_FAQ'),
                ],
                [
                    InlineKeyboardButton("Заказать Бокс", callback_data="Заказать Бокс"),
                    InlineKeyboardButton("Мои Боксы", callback_data="Мои Боксы"),
                    InlineKeyboardButton("Мои Заказы", callback_data="Мои Заказы"),
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

        def send_ful_name(update, context):
            chat_id = update.message.chat_id
            text = update.message.text
            profile_order[chat_id] = {
                    'nickname': update.message.from_user.username,
                    'name': text,
                }

            profile, _ = Client.objects.get_or_create(
                chat_id=chat_id,
                defaults={
                    'nickname': update.message.from_user.username,
                    'name': text,
                }
            )

            reply_text = '{}\n\nВведите ваш номер телефона: '.format(text)
            update.message.reply_text(text=reply_text)
            return 'PHONE_NUBER'

        def send_phone_number(update, _):
            print(profile_order)
            chat_id = update.message.chat_id
            text = update.message.text

            profile, _ = Client.objects.get_or_create(
                chat_id=chat_id,
                defaults={
                    'tel_number': text,
                }
            )

            reply_text = 'Введите ваш EMAIL: '
            update.message.reply_text(text=reply_text)
            return 'EMAIL'

        def send_email(update, _):
            chat_id = update.message.chat_id
            text = update.message.text

            profile, _ = Client.objects.get_or_create(
                chat_id=chat_id,
                defaults={
                    'email': text,
                }
            )

            reply_text = '''Подтвердите согласие на обработку персональных данных.
             Введите "Да" или "Нет'''
            update.message.reply_text(text=reply_text)
            return 'PERSONAL_DATA_CONSENT'

        def send_personal_data_consent(update, _):
            query = update.callback_query
            query.answer()
            chat_id = update.message.chat_id
            text = update.message.text
            if text.lower() == 'да':
                user_bool = True
                profile, _ = Client.objects.get_or_create(
                    chat_id=chat_id,
                    defaults={
                        'personal_data_consent_date': user_bool,
                    }
                )
                query.edit_message_text(text='Поздравляем с успешной регистрацией')
            else:
                user_bool = False
                profile, _ = Client.objects.get_or_create(
                    chat_id=chat_id,
                    defaults={
                        'personal_data_consent_date': user_bool,
                        'email': None,
                        'tel_number': None,
                        'name': None,
                    }
                )
                query.edit_message_text(text='Вы не согласились на обработку ПД. Ваши данные были удалены.')

            # reply_text = '''Поздравляем с успешной регистрацией'''
            # update.message.reply_text(text=reply_text)
            return 'MENU'

        def choose_plan(update, _):
            query = update.callback_query
            query.answer()
            keyboard = [
                [
                    InlineKeyboardButton("План 1", callback_data="FAQ_1"),
                    InlineKeyboardButton("План 2", callback_data="FAQ_2"),
                    InlineKeyboardButton("Назад", callback_data="to_start"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(
                text="Выберете интересующий план", reply_markup=reply_markup
            )

            return 'PLAN'

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

        def update_profile(update, _):
            query = update.callback_query
            query.answer()
            keyboard = [
                [
                    InlineKeyboardButton("Имя", callback_data="update_name"),
                    InlineKeyboardButton("Телефон", callback_data="update_phone"),
                    InlineKeyboardButton("Email", callback_data="update_email"),
                ],
                [
                    InlineKeyboardButton("Адрес доставки", callback_data="update_address"),
                    InlineKeyboardButton("Договор Оферты", callback_data="Договор Оферты"),
                    InlineKeyboardButton("Назад", callback_data="to_start"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(
                text="Введите ваше ФИО: ",  # reply_markup=reply_markup
            )
            return 'FULL_NAME'

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
            return 'GREETINGS'

        def send_field_info(update, _):
            query = update.callback_query
            query.edit_message_text(
                f'Обновялем {query.data} Введите новое значение'
            )
            return 'UPDATE'

        def update_field(update, _):
            user = update.message.from_user
            chat_instance = update.message.chat.id
            logger.info("Пользователь %s рассказал: %s", user.first_name, update.message.text)
            text = update.message.text
            update.message.reply_text(f'Спасибо! Вы ввели {text}')
            print(update)

            return 'BACK_TO_GREETINGS'

        def echo(update, context):
            # добавим в начало полученного сообщения строку 'ECHO: '
            text = 'ECHO: ' + update.message.text
            # `update.effective_chat.id` - определяем `id` чата,
            # откуда прилетело сообщение
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=text)
            print(update)

        def cancel(update, _):
            # определяем пользователя
            user = update.message.from_user
            # Пишем в журнал о том, что пользователь не разговорчивый
            logger.info("Пользователь %s отменил разговор.", user.first_name)
            # Отвечаем на отказ поговорить
            update.message.reply_text(
                'До новых встреч',
                reply_markup=ReplyKeyboardRemove()
            )
            # Заканчиваем разговор.
            return ConversationHandler.END

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start_conversation)],
            states={
                'GREETINGS': [
                    CallbackQueryHandler(choose_plan, pattern='^' + str(MENU) + '$'),
                    CallbackQueryHandler(faq, pattern='to_FAQ'),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                    CallbackQueryHandler(update_profile, pattern='to_profile'),
                    CallbackQueryHandler(update_form, pattern='(update_name|update_phone|update_email|update_address)'),
                    CallbackQueryHandler(send_field_info, pattern='update_field'),
                ],
                'UPDATE': [
                    MessageHandler(Filters.text & ~Filters.command, update_field)
                ],
                'BACK_TO_GREETINGS': [
                    CommandHandler('start', start_conversation)
                ],
                'SHOW_INFO': [
                    CallbackQueryHandler(faq,
                                         pattern='(FAQ_1|FAQ_2|FAQ_3|FAQ_4|FAQ_5|address|price|schedule|contacts)'),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                ],
                'FULL_NAME': [MessageHandler(Filters.text, send_ful_name)],
                'PHONE_NUBER': [MessageHandler(Filters.text, send_phone_number)],
                'EMAIL': [MessageHandler(Filters.text, send_email)],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )

        dispatcher.add_handler(conv_handler)

        updater.start_polling()
        updater.idle()
