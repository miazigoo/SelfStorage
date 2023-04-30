def get_client_contact_for_delivery(delivery):
    return f"""
Заказ:{delivery.order.pk} - {delivery.type.name}
---------------------------------------
Имя клиента: {delivery.order.client.name}
Aдрес: {delivery.order.client.address}
Номер телефона клиента: {delivery.order.client.tel_number}
"""


def get_client_contact_for_expired(today, order):
    return f"""
Заказ:{order.pk} - {(today - order.paid_up_to).days} дней просрочки
---------------------------------------
Имя клиента: {order.client.name}
Номер телефона клиента: {order.client.tel_number}
"""
