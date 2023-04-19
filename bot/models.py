from django.db import models


class Client(models.Model):
    chat_id = models.CharField(max_length=100, verbose_name='ID чата клиента')
    nickname = models.CharField(max_length=500, verbose_name='Никнейм пользователя')
    name = models.CharField(max_length=40, verbose_name='Имя пользователя', null=True, blank=True)
    tel_number = models.CharField(max_length=12, verbose_name='Номер телефона', null=True, blank=True, unique=True)
    email = models.EmailField(max_length=200, verbose_name='E-mail', blank=True, null=True, unique=True)
    created_at = models.DateTimeField(verbose_name='Создано', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Обновлено', auto_now=True)
    personal_data_consent = models.BooleanField(verbose_name='Согласие на ОПД', default=False)
    personal_data_consent_date = models.DateTimeField(auto_now_add=True,
                                                      verbose_name='Дата согласия на ОПД', blank=True, null=True)

    def __str__(self):
        return f'#{self.pk} {self.name} {self.nickname}'

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class ClientAddress(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE,
                               related_name='addresses', verbose_name='Клиент',
                               null=True, blank=True)
    address = models.TextField()

    def __str__(self):
        return f'{self.address} {self.client}'

    class Meta:
        verbose_name = 'Адрес клиента'
        verbose_name_plural = 'Адреса клиентов'


class Storage(models.Model):
    name = models.CharField(max_length=25, verbose_name='Название склада')
    address = models.TextField()

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Адрес склада'
        verbose_name_plural = 'Адреса складов'


class Box(models.Model):
    name = models.CharField(max_length=25, verbose_name='Обозначение')
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE, related_name='boxes', verbose_name='Склад')
    length = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()

    def __str__(self):
        return f'{self.name}({self.length}x{self.width}x{self.height})'

    class Meta:
        verbose_name = 'Бокс'
        verbose_name_plural = 'Боксы'


class BoxUsage(models.Model):
    box = models.ForeignKey(Box, on_delete=models.CASCADE, related_name='usages', verbose_name='Номер бокса')
    start_date = models.DateField(auto_now_add=True, verbose_name='Открыто')
    end_date = models.DateField(verbose_name='Закрыто')

    def __str__(self):
        return {self.box}


class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders', verbose_name='Клиент')
    created_at = models.DateTimeField(verbose_name='Создано', auto_now_add=True)
    box_usages = models.ManyToManyField(BoxUsage, through='BoxUsageByOrders', related_name='orders',
                                        verbose_name='Используемые боксы')

    def __str__(self):
        return f'#{self.pk} {self.client} {self.box_usages}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class BoxUsageByOrders(models.Model):
    box_usage = models.ForeignKey(BoxUsage, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.box_usage} {self.order}'


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
    address = models.ForeignKey(ClientAddress, on_delete=models.CASCADE,
                                related_name='deliveries', verbose_name='Адрес доставки')
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE,
                                related_name='deliveries', verbose_name='Адрес склада')
    status = models.ForeignKey(DeliveryStatus, on_delete=models.CASCADE,
                               related_name='deliveries', verbose_name='Статус')
    take_at = models.DateTimeField(verbose_name='Забрать в', null=True, blank=True)
    took_at = models.DateTimeField(verbose_name='Забрали в', null=True, blank=True)
    deliver_at = models.DateTimeField(verbose_name='Доставить в', null=True, blank=True)
    delivered_at = models.DateTimeField(verbose_name='Доставили в', null=True, blank=True)
    need_measurement = models.BooleanField(verbose_name='Требуются замеры')

    def __str__(self):
        if self.type == 'in':
            return f'#{self.pk}:{self.address}-{self.storage} {self.type}'
        elif self.type == 'out':
            return f'#{self.pk}:{self.storage}-{self.address} {self.type}'

    class Meta:
        verbose_name = 'Доставка'
        verbose_name_plural = 'Доставки'


class Payment(models.Model):
    box_usage_by_order = models.ForeignKey(BoxUsageByOrders, on_delete=models.CASCADE,
                                           verbose_name='Предмет платежа', related_name='payments')
    paid_days = models.IntegerField(verbose_name='Количество оплаченных дней')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата фиксации')

    def __str__(self):
        return f'#{self.pk} {self.box_usage_by_order} {self.paid_days} {self.created_at}'

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
