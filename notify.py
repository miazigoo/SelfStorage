from SelfStorage.wsgi import *
import datetime
import time

import environs
import schedule
from dateutil.relativedelta import relativedelta
from django.db import models
from pytz import timezone

from bot.models import Order
from email_sending import (
    send_email,
    get_subject_prior,
    get_message_prior,
    get_subject_expired,
    get_message_expired,
)

env = environs.Env()
env.read_env()


def send_notification_prior():
    today = datetime.datetime.now(timezone('UTC')).date()
    three_days_before = today + datetime.timedelta(days=3)
    two_weeks_before = today + datetime.timedelta(days=14)
    one_month_before = today + datetime.timedelta(days=30)
    orders = Order.objects.filter(
        end_storage_date__isnull=True,
    ).filter(
        models.Q(paid_up_to=three_days_before) |
        models.Q(paid_up_to=two_weeks_before) |
        models.Q(paid_up_to=one_month_before)
    )
    for order in orders:
        send_email(order, get_subject_prior(order), get_message_prior(order))

    print(f'Предварительные уведомления отправлены {datetime.datetime.now()}')


def send_notification_expired():
    today = datetime.datetime.now(timezone('UTC')).date()
    six_month_before = today - relativedelta(months=6)
    orders = Order.objects.filter(
        end_storage_date__isnull=True,
    ).filter(
        models.Q(paid_up_to__lt=today) &
        models.Q(paid_up_to__gt=six_month_before)
    )
    for order in orders:
        send_email(order, get_subject_expired(order), get_message_expired(order))
    print(f'Уведомления о просроченных заказах отправлены {datetime.datetime.now()}')

schedule.every().day.at("00:36", "UTC").do(send_notification_prior)
schedule.every(30).days.at("00:57", "UTC").do(send_notification_expired)


while True:
    schedule.run_pending()
    time.sleep(1)
