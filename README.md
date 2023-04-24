# Self Storage

Сервис по управлению складм

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
EMAIL_HOST_USER=YOUR_EMAIL_HOST_USER
EMAIL_HOST_PASSWORD=YOUR_EMAIL_HOST_PASSWORD
EMAIL_HOST=YOUR_EMAIL_HOST
EMAIL_PORT=YOUR_EMAIL_PORT
EMAIL_USE_TLS=YOUR_EMAIL_USE_TLS
EMAIL_USE_SSL=YOUR_EMAIL_USE_SSL
```

- Токен для Телеграм бота вы можете получить https://telegram.me/BotFather Чат ID можно узнать в свойствах канала
- Не забудьте прописать команду `/setinline.`а так же задайте описание бота через `/setdescription`



