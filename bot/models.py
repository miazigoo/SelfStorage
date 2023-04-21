from django.db import models


class Client(models.Model):
    chat_id = models.CharField(max_length=100, verbose_name='ID чата клиента')
    nickname = models.CharField(max_length=500, verbose_name='Никнейм клиента')
    name = models.CharField(max_length=40, verbose_name='Имя клиента', null=True, blank=True)
    tel_number = models.CharField(max_length=12, verbose_name='Номер телефона', null=True, blank=True, unique=True)
    email = models.EmailField(max_length=200, verbose_name='E-mail', blank=True, null=True, unique=True)
    created_at = models.DateTimeField(verbose_name='Создано', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Обновлено', auto_now=True)
    personal_data_consent = models.BooleanField(verbose_name='Согласие на ОПД', default=False)
    personal_data_consent_date = models.DateTimeField(auto_now_add=True,
                                                      verbose_name='Дата согласия на ОПД', blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'#{self.pk} {self.name} {self.nickname}'

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class Storage(models.Model):
    name = models.CharField(max_length=25, verbose_name='Название склада')
    address = models.TextField()

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склады'


class Box(models.Model):
    name = models.CharField(max_length=25, verbose_name='Обозначение')
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE, related_name='boxes', verbose_name='Склад')
    length = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()

    def __str__(self):
        return f'{self.name}({self.length}x{self.width}x{self.height} м)'

    class Meta:
        verbose_name = 'Бокс'
        verbose_name_plural = 'Боксы'


class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders', verbose_name='Клиент')
    created_at = models.DateTimeField(verbose_name='Создано', auto_now_add=True)
    box = models.ForeignKey(Box, on_delete=models.CASCADE, related_name='orders',
                            verbose_name='Бокс', null=True, blank=True)
    start_storage_date = models.DateField(auto_now_add=True, verbose_name='Открыто', null=True, blank=True)
    end_storage_date = models.DateField(verbose_name='Закрыто', null=True, blank=True)
    paid_up_to = models.DateField(verbose_name="Оплачено до", null=True, blank=True)
    weight = models.CharField(max_length=50, verbose_name='Вес', null=True, blank=True)
    size = models.CharField(max_length=50, verbose_name='Размер', null=True, blank=True)
    things = models.TextField(max_length=50, verbose_name='Список вещей', null=True, blank=True)
    title = models.CharField(max_length=200, verbose_name='Название заказа', null=True, blank=True)
    delivery_type = models.CharField(max_length=25, verbose_name="Тип доставки", null=True, blank=True)

    def get_description(self):
        if self.things:
            things = self.things
        else:
            things = "Список вещей не был указан"
        return f"""
        {things}
        
        общий вес: {self.weight}
        
        общий размер: {self.size}
        """

    def __str__(self):
        return f'#{self.pk} {self.client} {self.box}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class DeliveryStatus(models.Model):
    name = models.CharField(max_length=10, verbose_name="Название статуса доставки")

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Статус доставки'
        verbose_name_plural = 'Статусы доставки'


delivery_types = (
    ('in', 'на хранение'),
    ('out', 'с хранения')
)


class Delivery(models.Model):
    type = models.CharField(max_length=10, choices=delivery_types, verbose_name='Тип доставки')
    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              related_name='deliveries', verbose_name='Заказ')
    status = models.ForeignKey(DeliveryStatus, on_delete=models.CASCADE,
                               related_name='deliveries', verbose_name='Статус')
    take_at = models.DateTimeField(verbose_name='Забрать в', null=True, blank=True)
    took_at = models.DateTimeField(verbose_name='Забрали в', null=True, blank=True)
    deliver_at = models.DateTimeField(verbose_name='Доставить в', null=True, blank=True)
    delivered_at = models.DateTimeField(verbose_name='Доставили в', null=True, blank=True)
    need_measurement = models.BooleanField(verbose_name='Требуются замеры')
    created_at = models.DateTimeField(verbose_name='Создано', auto_now_add=True)

    def __str__(self):
        return f'#{self.pk}:{self.order} {self.type}'

    class Meta:
        verbose_name = 'Доставка'
        verbose_name_plural = 'Доставки'
