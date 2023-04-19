from django.contrib import admin
from .models import *


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'nickname', 'tel_number']


@admin.register(ClientAddress)
class ClientAddressAdmin(admin.ModelAdmin):
    list_display = ['client', 'address']


@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(BoxUsage)
class BoxUsageAdmin(admin.ModelAdmin):
    list_display = ['box', 'start_date', 'end_date']


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ['name', 'storage']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    raw_id_fields = ('box_usages',)
    list_display = ['client']


@admin.register(BoxUsageByOrders)
class BoxUsageByOrdersAdmin(admin.ModelAdmin):
    pass


@admin.register(DeliveryStatus)
class DeliveryStatusAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['type', 'address']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['box_usage_by_order', 'paid_days', 'created_at']
