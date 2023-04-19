from django.db import models


class Profile(models.Model):
    external_id = models.PositiveIntegerField(verbose_name='Внешний ID пользователя', unique=True)
    name = models.CharField(max_length=1000, verbose_name='Имя пользователя')

    def __str__(self):
        return f'#{self.external_id} {self.name}'

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class User(models.Model):
    chat_id = models.CharField(max_length=100, verbose_name="ID чата клиента")
    name = models.CharField(max_length=40, verbose_name="Имя пользователя", null=True, blank=True)
    tel_number = models.CharField(max_length=10, verbose_name="Номер телефона", null=True, blank=True, unique=True)
    email = models.EmailField(max_length=70, verbose_name="E-mail", blank=True, null=True, unique=True)
    created_at = models.DateTimeField(verbose_name="Создано", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Обновлено", auto_now=True)
    personal_data_consent = models.BooleanField(verbose_name="Согласие на ОПД", default=False)
    personal_data_consent_date = models.DateTimeField(verbose_name="Дата согласия на ОПД", blank=True, null=True)

    def __str__(self):
        return f'#{self.pk} {self.name}'

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class User_address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='Клиент', null=True, blank=True)
    address = models.TextField()

    def __str__(self):
        return f'{self.address}'

    class Meta:
        verbose_name = 'Адрес клиента'
        verbose_name_plural = 'Адреса клиентов'


class Storage(models.Model):
    name = models.CharField(max_length=25, verbose_name="Название склада")
    address = models.TextField()

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Адрес склада'
        verbose_name_plural = 'Адреса складов'

class Box(models.Model):
    name = models.CharField(max_length=25, verbose_name='Обозначение')
    storage_id = models.ForeignKey(Storage, on_delete=models.CASCADE, related_name='boxes', verbose_name="Склад")
    length = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()

    def __str__(self):
        return f'{self.name}({self.length}x{self.width}x{self.height})'

    class Meta:
        verbose_name = 'Бокс'
        verbose_name_plural = 'Боксы'


class Box_usage(models.Model):
    box = models.ForeignKey(Box, on_delete=models.CASCADE, related_name='usages', verbose_name="Номер бокса")
    start_date = models.DateField(auto_now_add=True, verbose_name="Открыто")
    end_date = models.DateField(verbose_name="Закрыто")


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='Клиент')
    created_at = models.DateTimeField(verbose_name="Создано", auto_now_add=True)
    boxes = models.ManyToManyField(Box_usage, through="Order_box_usage", related_name="orders", verbose_name="Используемые боксы")

    def __str__(self):
        return f'#{self.pk}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class Order_box_usage(models.Model):
    box_usages = models.ForeignKey(Box_usage, on_delete=models.CASCADE)
    orders = models.ForeignKey(Order, on_delete=models.CASCADE)

