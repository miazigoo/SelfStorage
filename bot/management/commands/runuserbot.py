import logging
from django.core.management.base import BaseCommand
from django.conf import settings
import environs
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

# Этапы/состояния разговора
FIRST, SECOND = range(2)
# Данные обратного вызова
ONE, TWO, THREE, FOUR = range(4)

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
                    text="Выберете интресующий вас вопрос", reply_markup=reply_markup
                )
            return 'GREETINGS'

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
            print('faq ')
            query = update.callback_query
            query.answer()
            keyboard = [
                [
                    InlineKeyboardButton("FAQ_1", callback_data='FAQ_1'),
                    InlineKeyboardButton("FAQ_2", callback_data='FAQ_2'),
                    InlineKeyboardButton("Назад", callback_data="to_start"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(
                text="Выберете интересующий вопрос", reply_markup=reply_markup
            )
            return 'GREETINGS'

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
                text="Выберете интересующий вопрос", reply_markup=reply_markup
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
                    CallbackQueryHandler(choose_plan, pattern='^' + str(ONE) + '$'),
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
                ]
            },
            fallbacks = [CommandHandler('cancel', cancel)]
        )

        dispatcher.add_handler(conv_handler)

        # echo_handler = MessageHandler(Filters.text, echo)
        # dispatcher.add_handler(echo_handler)

        updater.start_polling()
        updater.idle()




if __name__ == '__main__':
    env = environs.Env()
    env.read_env()


    print('olol')