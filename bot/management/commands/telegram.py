
from bot.models import Profile

from django.core.management import BaseCommand
from environs import Env
from telegram.ext import CommandHandler
from telegram.ext import CallbackContext
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater
from telegram import Bot
from telegram import Update
from telegram.utils.request import Request

env = Env()
env.read_env()

tg_token = env.str('TG_TOKEN')


def log_errors(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            error_message = f'Произошла ошибка: {e}'
            print(error_message)
            raise e

    return inner


@log_errors
def do_echo(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text

    profile, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': update.message.from_user.username,
        }
    )

    reply_text = 'Ваш ID = {}\n\n{}'.format(chat_id, text)
    update.message.reply_text(text=reply_text)


class Command(BaseCommand):
    help = 'Телеграм-бот'

    def handle(self, *args, **options):
        #  1 -- Правильное подключение
        request = Request(connect_timeout=0.5, read_timeout=1.0, )
        bot = Bot(request=request, token=tg_token, )
        print(bot.get_me())

        #  2 -- Обработчики
        # получаем экземпляр `Updater`
        updater = Updater(bot=bot, use_context=True)

        def start(update, context):
            """ Команда запуска бота """
            # `bot.send_message` это метод Telegram API
            # `update.effective_chat.id` - определяем `id` чата,
            # откуда прилетело сообщение
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="I'm a bot, please talk to me!")

        def unknown(update, context):
            """ Не распознанные команды """
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Sorry, I didn't understand that command.")

        start_handler = CommandHandler('start', start)
        message_handler = MessageHandler(Filters.text, do_echo)
        updater.dispatcher.add_handler(start_handler)
        # updater.dispatcher.add_handler(CommandHandler("start", commands.command_start))
        # updater.dispatcher.add_handler(message_handler)

        unknown_handler = MessageHandler(Filters.command, unknown)
        updater.dispatcher.add_handler(unknown_handler)
        #  3 -- Запустить бесконечную обработку сообщений
        updater.start_polling()
        updater.idle()
