from django.contrib import admin
from .models import *


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'nickname', 'tel_number']


@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ['name', 'storage', 'length', 'width', 'height']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    raw_id_fields = ('box',)
    list_display = ['client']


@admin.register(DeliveryStatus)
class DeliveryStatusAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['type', 'order']


@admin.register(DeliveryType)
class DeliveryTypeAdmin(admin.ModelAdmin):
    list_display = ['name']
