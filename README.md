# SelfStorage

SelfStorage - это сервис, который предоставляет Заказчику возможность сдавать в аренду складские помещения через
чат - бот в телеграм. 

С помощью этого сервиса пользователи могут арендовать склады,
оформлять бесплатный вывоз вещей на склад, заказывать бесплатную доставку вещей до склада,
получать напоминания о завершении срока аренды, а также о забытых на складе вещах.Также в чат - боте реализован FAQ,
который позволяет клиентам быстро получить ответы на самые частые вопросы.

Заказчик прямо через бота в телеграм  может просматирвать статистику по рекламным кампаниям, просматривать перечень заказов на доставку вещей на
склад или со склада, а также просматривать список заказов, у которых закончился срок хранения.

### Как установить
Для запуска сайта вам понадобится Python третьей версии.

Скачайте код с GitHub. Установите зависимости:

```sh
pip install -r requirements.txt
```

Создайте базу данных SQLite

```sh
python3 manage.py makemigrations
python3 manage.py migrate
```
Для корректной работы в БД должен существовать склад и хотя бы 1 бокс

Перед установкой создайте файл **.env** вида:
```properties
TG_TOKEN=YOUR_TG_TOKEN
TG_TOKEN_ADMIN=YOUR_NEXT_TG_TOKEN
BITLY_TOKEN=YOUR_BITLY_TOKEN
```
для работы почтовых уведомлений добавьте:
```
EMAIL_HOST_USER=YOUR_EMAIL_HOST_USER
EMAIL_HOST_PASSWORD=YOUR_EMAIL_HOST_PASSWORD
EMAIL_HOST=YOUR_EMAIL_HOST
EMAIL_PORT=YOUR_EMAIL_PORT
EMAIL_USE_TLS=YOUR_EMAIL_USE_TLS
EMAIL_USE_SSL=YOUR_EMAIL_USE_SSL
```

- Токен для Телеграм бота вы можете получить [по ссылке](https://telegram.me/BotFather). Чат ID можно узнать в свойствах канала.
- Не забудьте прописать команду `/setinline`, а так же задайте описание бота через `/setdescription`.

- Схему базы данных можно посмотреть [по ссылке](https://drawsql.app/teams/selfstorage-project/diagrams/selfstorage).

### Как настроить под себя

- Вы можете поменять приветственное сообщение в файле ```hello.txt``` в папке  ```bot```.
- Ответы на FAQ можно поменять в файле ```faq_answers.py```.
- Изменить время отправки уведомлений можно в файле ```notify.py```
- Изменить шаблоны сообщений владельцу склада о доставках и просроченных заказа можно в файле ```text_templates.py```
- Изменить шаблоны уведомлений клиента по электронной почте можно в файле ```email_sending.py```

### Как использовать

Следующая команда запускает бота для пользователя:
```
python manage.py runuserbot
```
- Следующая команда запускает бота для владельца склада:
```commandline
python manage.py adminbot
```
- Следующая команда запускает планировщика для отправки уведомлений:
```commandline
python notify.py
```
