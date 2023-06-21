
import smtplib

from django.conf import settings
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dateutil.relativedelta import relativedelta


def send_email(order, subject, message):
    fromaddr = settings.EMAIL_HOST_USER
    toaddr = order.client.email
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject
    body = message
    msg.attach(MIMEText(body, 'html'))
    server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
    server.starttls()
    server.login(fromaddr, settings.EMAIL_HOST_PASSWORD)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()


def get_subject_prior(order):
    return f'Заказ №{order.pk} - заканчивается хранение'


def get_subject_expired(order):
    return f'Заказ №{order.pk} - закончилось хранение'


def get_message_prior(order):
    return """
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="UTF-8">
        <title>Важное уведомление от нашей компании</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            font-size: 20px;
            line-height: 1.5;
          }
          .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            border: 1px solid #ccc;
            border-radius: 10px;
          }
          .logo {
            font-size: 26px;
            font-weight: bold;
            text-align: center;
            letter-spacing: 2px;
            color: #333;
            margin-top: 10px;
            }
          .message {
            margin-bottom: 20px;
          }
          .cta {
            text-align: center;
          }
          .cta a {
            display: inline-block;
            padding: 10px 20px;
            background-color: #337ab7;
            color: #fff;
            text-decoration: none;
            border-radius: 5px;
          }
          .footer {
            text-align: center;
            font-size: 14px;
            color: #777;
            line-height: 0.5;
          }
        </style>
      </head>""" + f"""
      <body>
        <div class="container">
          <div class="logo">SelfStorage</div>
          <div class="message">
            <p>Уважаемый клиент,</p>
            <p>Хотим напомнить, что срок хранения Вашего заказа заканчивается
            <strong>{order.paid_up_to.strftime("%d.%m.%Y")}</strong>.</p>
            <p>Пожалуйста, своевременно продлите хранение Ваших вещей или заберите их,
             чтобы избежать дополнительных расходов.</p>
          </div>
          <div class="cta">
            <a href="https://t.me/test_python_zeder_bot">Перейти в чат-бот</a>
          </div>
          <div class="footer">
            <p>С уважением,</p>
            <p>компания SelfStorage</p>
          </div>
        </div>
      </body>
    </html>
    """


def get_message_expired(order):
    return """
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="UTF-8">
        <title>Важное уведомление от нашей компании</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            font-size: 20px;
            line-height: 1.5;
          }
          .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            border: 1px solid #ccc;
            border-radius: 10px;
            }
          .logo {
            font-size: 26px;
            font-weight: bold;
            text-align: center;
            letter-spacing: 2px;
            color: #333;
            margin-top: 10px;
            }
          .message {
            margin-bottom: 20px;
          }
          .cta {
            text-align: center;
          }
          .cta a {
            display: inline-block;
            padding: 10px 20px;
            background-color: #337ab7;
            color: #fff;
            text-decoration: none;
            border-radius: 5px;
          }
          .footer {
            text-align: center;
            font-size: 14px;
            color: #777;
            line-height: 0.5;
          }
        </style>
      </head>""" + f"""
      <body>
        <div class="container">
          <div class="logo">SelfStorage</div>
          <div class="message">
            <p>Уважаемый клиент,</p>
            <p>Хотим напомнить, что срок хранения Вашего заказа №{order.pk} закончился
            <strong>{order.paid_up_to.strftime("%d.%m.%Y")}</strong>.</p>
            <p>Мы будем хранить Ваши вещи еще в течение полугода после окончания срока хранения до
             <strong>{ (order.paid_up_to + relativedelta(months=6)).strftime('%d.%m.%Y')}</strong>
            Пожалуйста, заберите свои вещи в ближайшее время или продлите срок хранения.
            После <strong>{ (order.paid_up_to + relativedelta(months=6)).strftime('%d.%m.%Y')}</strong> мы будем
            вынуждены утилизировать Ваши вещи.</p>
            <p>Спасибо за использование услуг нашей компании.</p>
          </div>
          <div class="cta">
            <a href="https://t.me/TestButtonsNatBot">Перейти в чат-бот</a>
          </div>
          <div class="footer">
            <p>С уважением,</p>
            <p>компания SelfStorage</p>
          </div>
        </div>
      </body>
    </html>
    """
