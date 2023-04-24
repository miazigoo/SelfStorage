from SelfStorage.wsgi import *
import celery
from django.core.mail import send_mail
import datetime
from pytz import timezone
from bot.models import Order
from django.db import models
import environs
from dateutil.relativedelta import relativedelta

env = environs.Env()
env.read_env()

@celery.shared_task
def send_notification():
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
        subject = f'Заказ № {order.pk}'
        message = f'Уважаемый, клиент! Срок хранения Вашего заказа заканчивается {order.paid_up_to}.\
        Просим своевременно продлить хранение Ваших вещей или забрать их.'
        send_mail(
            subject,
            message,
            env('EMAIL_HOST_USER'),
            [order.client.email],
        )

@celery.shared_task
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
        subject = f'Заказ № {order.pk}'
        message = f'Уважаемый, клиент! Срок хранения Вашего заказа закончился {order.paid_up_to}.\
Ваши вещи будут хранится у нас еще полгода от этой даты. ' \
f'Если Вы не заберете их до {order.paid_up_to + relativedelta(months=6)}, они будут утилизированы.'
        send_mail(
            subject,
            message,
            env('EMAIL_HOST_USER'),
            [order.client.email],
        )
