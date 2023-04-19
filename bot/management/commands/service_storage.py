from django.core.management import BaseCommand
from environs import Env
from telegram.ext import Updater


class Command(BaseCommand):
    help = 'Телеграм-бот'

    def handle(self, *args, **options):
        env = Env()
        env.read_env()

        tg_token = env.str('TG_TOKEN')
        updater = Updater(token=tg_token)

        dispatcher = updater.dispatcher
