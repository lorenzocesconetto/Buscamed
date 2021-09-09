from flask import render_template, current_app
from app.email import send_email


def send_admins_order_notification_email(order):
    send_email('[BuscaMed] Novo Pedido',
               sender=current_app.config['FLASKY_MAIL_SENDER'],
               recipients=current_app.config['DELIVERY_EMAILS'],
               text_body=render_template('email/order.txt', order=order),
               html_body=render_template('email/order.html', order=order))


def send_customer_order_confirmation_email(order, user):
    send_email('[BuscaMed] Confirmação de Pedido',
               sender=current_app.config['FLASKY_MAIL_SENDER'],
               recipients=[user.email],
               text_body=render_template(
                   'email/customer_purchase.txt', order=order, user=user),
               html_body=render_template(
                   'email/customer_purchase.html', order=order, user=user)
               )
