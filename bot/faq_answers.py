from bot.models import Storage

storage = Storage.objects.all()[0]

FAQ_ANSWERS = {
    'FAQ_что_хранить': '''Можно хранить:

🪑 мебель,

📚 книги,

📦 бытовую технику,

👗 одежду,

👞 обувь,

🏍️ мотоцикл,

🚴‍ велосипед,

🛞 шины

и многие другие вещи можно сдать на время в хранилище SelfStorage.''',
    'FAQ_нельзя_хранить': '''Нельзя хранить:
🍧 скоропортящиеся продукты,

💍 ювелирные изделия,

🧨 воспламеняющиеся и взрывоопасные вещества,

🎭 предметы искусства и другие вещи, которые требуют специальных условий хранения,

📲 электронику (айфоны, айпэды и другие устройства, излучающие электромагнитные волны и передающие информацию),

⚛️ химические и горюче-смазочные вещества,

🎨 промышленные и бытовые краски в негерметичной упаковке или ранее вскрытой упаковке,

💧 жидкости, кроме закрытых герметично,

🔫 наркотики, оружие, боеприпасы и другие вещи,
запрещенные законом РФ или подлежащие изъятию у владельца по решению суда,

🌱 растения,

🐕 животных или чучела животных
                   ''',
    'FAQ_как_храним': '''Мы храним Ваши вещи на тёплом и безопасном складе с постоянной температурой 20 градусов.
Для хранения велосипедов, сноубордов и лыж мы предоставляем крепления, для коробок можем предосталять стеллажи. ''',
    'FAQ_оформить_хранение': '''Для оформления заказа воспользуйтесь разделом меню "Заказать бокс" в нашем боте,
и ответе на его вопросы. ''',
    'FAQ_забрать_вещи': '''Из главного меню бота перейдите -> Мои боксы -> Выберете нужный бокс, после чего выберите ->
Забрать вещи, дальше будет выбор оформления доставки или самовывоза.
При самовыозе для получения вещей будет сгенерирован QR код''',
    'FAQ_address': f'''Наш склад находится по адресу:\n  {storage.address} ''',
    'FAQ_price': ''' Мы измеряем габариты ваших вещей на месте и рассчитываем объём в кубических метрах.
Габариты вещей сложной формы, таких как диван, кресло или стул,
мы измеряем по размеру описанного вокруг них прямоугольника.
Муверы сразу сообщат вам итоговый тариф, и вы сможете подтвердить его или изменить количество вещей.''',
    'FAQ_schedule': 'Мы работаем круглосуточно',
    'FAQ_contacts': 'Наш контактный телефон ХХХХХХХХХХ',
    'FAQ_forget': '''Ваши вещи будут храниться 6 месяцев по установленному ранее тарифу с 10% надбавкой,
после этого, если Вы их так и не заберете – Вы их потеряете.''',
}
