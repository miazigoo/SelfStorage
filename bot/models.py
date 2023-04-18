from django.db import models


class Profile(models.Model):
    external_id = models.PositiveIntegerField(verbose_name='Внешний ID пользователя', unique=True)
    name = models.CharField(max_length=1000, verbose_name='Имя пользователя')

    def __str__(self):
        return f'#{self.external_id} {self.name}'

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
