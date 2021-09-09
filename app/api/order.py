from app.telegram import telegram_new_order
from flask_login import current_user
from app.api import rest_api, authentication
from app import db
from flask_restful import Resource, reqparse, fields, marshal_with
from app.models import Order
import demjson
import re
from app.api.email import send_admins_order_notification_email, send_customer_order_confirmation_email
from app.decorators import delivery_required

orders_fields = {
    'id': fields.Integer,
    'placed_timestamp': fields.DateTime,
    'payment_method': fields.Nested({'name': fields.String}),
    'total': fields.Float,
    'frontend_total': fields.Float,
    'canceled': fields.Boolean,
    'user': fields.Nested(
        {
            'name': fields.String,
            "cep": fields.String,
            'phone': fields.String,
            "logradouro": fields.String,
            "complemento": fields.String,
            "bairro": fields.String,
        }
    )
}


class Orders(Resource):
    # @delivery_required
    # @authentication.login_required
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('order_id', type=int, required=True)
        args = parser.parse_args(strict=True)
        order = Order.query.get(args['order_id'])
        try:
            order.delivered = True
            db.session.add(order)
            db.session.commit()
            return {}, 200
        except:
            db.session.rollback()
            return {}, 400

    # @authentication.login_required
    # @delivery_required
    @marshal_with(orders_fields)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default=1)
        args = parser.parse_args(strict=True)
        return Order.query.filter_by(delivered=False, canceled=False).order_by(Order.placed_timestamp).paginate(args['page'], 20, False).items

    # @authentication.login_required
    def post(self):
        if not current_user.is_authenticated:
            return {'message': 'Por favor faça login ou cadastre-se gratuitamente para realizar compras'}, 401
        parser = reqparse.RequestParser()
        parser.add_argument('cart', required=True)
        parser.add_argument('payment', type=str, required=True)
        parser.add_argument('total', type=float, required=True)
        args = parser.parse_args(strict=True)

        args['cart'] = re.sub(r'\bNone\b', 'null', args['cart'])
        args['cart'] = demjson.decode(args['cart'])

        order, success, message = Order.process_order(args)
        if success:
            send_admins_order_notification_email(order=order)
            send_customer_order_confirmation_email(
                order=order, user=current_user)
            # telegram_new_order(order)
            return dict(), 200
        return {'message': message}, 400


rest_api.add_resource(Orders, '/order')
