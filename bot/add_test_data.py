from SelfStorage.wsgi import *
from bot.models import (
    Advertisement,
    Client,
    Order,
    Storage,
    Box,
    DeliveryType,
    DeliveryStatus,
    Delivery,
)
import datetime


# DeliveryType.objects.create(name='забрать вещи у клиента')
# DeliveryType.objects.create(name='отвезти вещи клиенту')
# DeliveryStatus.objects.create(name='создано')
# Client.objects.create(
#     chat_id='233456',
#     nickname='greenBase',
#     name='Николай',
#     tel_number='+7(926)541-45-16',
#     email='kolya@gmail.com',
#     personal_data_consent=True,
#     address='Москва, ул. Кременчугская, д.12, кв. 192'
# )
# Client.objects.create(
#     chat_id='567903',
#     nickname='newcroc',
#     name='Светлана',
#     tel_number='+7(916)324-90-09',
#     email='sveta@gmail.com',
#     personal_data_consent=True,
#     address='Москва, ул. 50-ти летия Октября, д. 118, кв. 24'
# )
# Storage.objects.create(
#     name='Основной склад',
#     address='Москва, ул. Островитянова, д.9, корп.3',
# )
# Box.objects.create(
#     name='A1',
#     length=3,
#     width=1,
#     height=2,
#     storage=Storage.objects.get(pk=1),
# )
# Box.objects.create(
#     name='A2',
#     length=2,
#     width=1,
#     height=2,
#     storage=Storage.objects.get(pk=1),
# )
# Box.objects.create(
#     name='B1',
#     length=2,
#     width=1.5,
#     height=1.5,
#     storage=Storage.objects.get(pk=1),
# )
# Box.objects.create(
#     name='B2',
#     length=5,
#     width=3,
#     height=2,
#     storage=Storage.objects.get(pk=1),
# )
# Order.objects.create(
#     client=Client.objects.get(pk=1),
#     start_storage_date=datetime.date(2023, 1, 1),
#     paid_up_to=datetime.date(2023, 4, 11),
#     weight='до 10 кг',
#     size='3 - 7 куб.м',
#     things='Зимние куртки, архив фотографий, учебники за 5-й класс, елка и елочные игрушки',
#     title='Всякая мелочь (в т.ч. зима)',
# )
# Order.objects.create(
#     client=Client.objects.get(pk=1),
#     start_storage_date=datetime.date(2023, 4, 15),
#     paid_up_to=datetime.date(2023, 6, 15),
#     weight='25-50 кг',
#     size='3 - 7 куб.м',
#     things='Диван и куча коробок',
#     title='Диван',
# )
# Delivery.objects.create(
#     need_measurement = False,
#     order=Order.objects.get(pk=1),
#     status=DeliveryStatus.objects.get(pk=1),
#     type=DeliveryType.objects.get(pk=1)
# )
# Delivery.objects.create(
#     need_measurement = False,
#     order=Order.objects.get(pk=2),
#     status=DeliveryStatus.objects.get(pk=1),
#     type=DeliveryType.objects.get(pk=1)
# )
# Advertisement.objects.create(
#     name='Первая кампания',
#     url='bit.ly/3YR47zU',
# )
# Advertisement.objects.create(
#     name='Реклама в вк',
#     url='bit.ly/ivrimiliya',
# )
# Advertisement.objects.create(
#     name='Листовки',
#     url='bitly.is/3mJB1VF',
# )
# Client.objects.create(
#     chat_id='248210561',
#     nickname='@nkashaeva',
#     name='Наталия',
#     tel_number='+7(926)561-49-36',
#     email='n.a.kashaeva@gmail.com',
#     personal_data_consent=True,
#     address='Москва, просп. Андропова, 18, корп. 7, кв. 155'
# )
# Order.objects.create(
#     client=Client.objects.get(pk=3),
#     start_storage_date=datetime.date(2023, 1, 18),
#     paid_up_to=datetime.date(2023, 5, 18),
#     weight='25-50 кг',
#     size='3 - 7 куб.м',
#     things='Чемоданы, палатки, котелок, спальники',
#     title='Чемоданы',
# )
# Order.objects.create(
#     client=Client.objects.get(pk=3),
#     start_storage_date=datetime.date(2023, 4, 18),
#     paid_up_to=datetime.date(2023, 11, 18),
#     weight='25-50 кг',
#     size='3 - 7 куб.м',
#     things='Шины, ватрушка, сноуборд',
#     title='Шины и пр.',
# )