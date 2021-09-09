import telegram_send
from dateutil import tz

# from_zone = tz.gettz('UTC')
to_zone = tz.gettz('America/Sao_Paulo')

def telegram_message(message: str):
    telegram_send.send(messages=[message])


def telegram_new_order(order):
    time = order.placed_timestamp.astimezone(to_zone)
    formatted_time = time.strftime('%d/%m/%Y %H:%M')
    text = f'{order.id} - NOVO PEDIDO de {order.user.name} às {formatted_time}'
    telegram_send.send(messages=[text])

