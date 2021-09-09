from datetime import datetime
from time import time
from flask import current_app
from flask.globals import session
from flask_login import UserMixin, AnonymousUserMixin, current_user
from unidecode import unidecode
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login_manager
from app.search import add_to_index, remove_from_index, query_index
from sqlalchemy import func, and_
from sqlalchemy.orm import aliased
from app.constants import DELIVERY_FEE
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from decimal import Decimal


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        eans, total = query_index(
            cls.__tablename__, expression, page, per_page)
        if total == 0:
            return dict(), 0

        when = []
        for i, ean in enumerate(eans):
            when.append((ean, i))

        items = cls.get_best_prices(eans).order_by(db.case(when, value=cls.id))

        return items, total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


class DeliveryMethod:
    IN_STORE = 1
    TO_ADDRESS = 2


class Payment:
    CASH = 1
    DEBIT_CARD = 2
    CREDIT_CARD = 3


class OrderItems(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey(
        'order.id'), nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey(
        'item.id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(precision=8, scale=2), nullable=False)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id'), index=True, nullable=False)
    placed_timestamp = db.Column(
        db.DateTime, default=datetime.utcnow, index=True, nullable=False)
    payment_method_id = db.Column(
        db.Integer, db.ForeignKey('payment_method.id'), nullable=False)
    cash_value = db.Column(db.Numeric(precision=8, scale=2))
    delivery_method = db.Column(db.Integer)
    delivery_fee = db.Column(db.Numeric(precision=8, scale=2), nullable=False)
    total = db.Column(db.Numeric(precision=8, scale=2), nullable=False)
    frontend_total = db.Column(db.Numeric(
        precision=8, scale=2), nullable=False)
    assigned_deliveryman = db.Column(db.Boolean, nullable=False, default=False)
    delivered = db.Column(db.Boolean, nullable=False, default=False)
    delivered_timestamp = db.Column(db.DateTime, index=True)
    order_items = db.relationship(
        'OrderItems', backref='order', lazy='dynamic')
    canceled = db.Column(db.Boolean, nullable=False, default=False)

    @staticmethod
    def process_order(data):
        if data['payment'] == "debito":
            payment = Payment.DEBIT_CARD
        elif data['payment'] == "credito":
            payment = Payment.CREDIT_CARD
        elif data['payment'] == "dinheiro":
            payment = Payment.CASH
        else:
            return None, False, 'Meio de pagamento invalido'
        if len(data['cart'].keys()) == 0:
            return None, False, 'Não há produtos no pedido'

        order = Order(payment_method_id=payment, total=0,
                      user=current_user, delivery_fee=0, frontend_total=data['total'])

        order_items = list()
        total_price = Decimal(DELIVERY_FEE)
        for key, value in data['cart'].items():
            item = Item.query.get(key)
            if not item:
                return None, False, 'Item nao encontrado'
            item_total_price = 0
            if item.promotion_price and item.promotion_qty:
                promotion_units = (
                    value['quantity'] // item.promotion_qty) * item.promotion_qty
                regular_units = value['quantity'] % item.promotion_qty
                item_total_price += Decimal(promotion_units *
                                            item.promotion_price + regular_units * item.price)
                total_price += item_total_price
            else:
                item_total_price += value['quantity'] * item.price
                total_price += Decimal(item_total_price)
            unit_price = item_total_price / value['quantity']
            order_items.append(OrderItems(order=order, item=item, unit_price=unit_price, quantity=value['quantity']
                                          ))

        order.total = total_price
        try:
            db.session.rollback()
            db.session.add(order)
            db.session.add_all(order_items)
            db.session.commit()
            return order, True, 'Pedido processado com sucesso'
        except:
            db.session.rollback()
            return None, False, 'Erro inesperado'


class ProductDetailClick(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ean = db.Column(db.BigInteger, primary_key=False,
                    nullable=False, autoincrement=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id'), index=True, nullable=True)

    @staticmethod
    def click(ean):
        obj = ProductDetailClick(ean=ean)
        if current_user.is_authenticated:
            obj.user = current_user
        db.session.add(obj)
        db.session.commit()


class Searches(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    search = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id'), index=True, nullable=True)

    @staticmethod
    def add_search(text):
        text = unidecode(text.lower().strip())
        obj = Searches(search=text)
        if current_user.is_authenticated:
            obj.user = current_user
        db.session.add(obj)
        db.session.commit()


class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False, unique=True)
    address = db.Column(db.String(256))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    is_ecommerce = db.Column(db.Boolean, nullable=False, default=True)
    own_delivery = db.Column(db.Boolean, nullable=False,
                             default=False, server_default="false")
    buscamed_delivery = db.Column(
        db.Boolean, nullable=False, default=False, server_default="false")
    phone = db.Column(db.String(19))
    is_active = db.Column(db.Boolean, server_default="true",
                          default=True, nullable=False)
    items = db.relationship('Item', backref='store', lazy='dynamic')
    users = db.relationship('User', backref='store', lazy='dynamic')

    def __repr__(self) -> str:
        return f'<Store {self.name} {self.id}'

    def __str__(self) -> str:
        return self.name


def update_timestamp(context):
    update_keys = context.current_parameters.keys()
    is_active_keys = ['is_active', 'timestamp', 'item_id']
    # If only is active was updated
    if set(update_keys) == set(is_active_keys):
        item = Item.query.get(context.current_parameters['item_id'])
        return item.timestamp
    return datetime.utcnow()


class Item(SearchableMixin, db.Model):
    __searchable__ = ['name', 'id', 'store_id', 'is_active']
    __table_args__ = (db.UniqueConstraint(
        'ean', 'store_id', name='_ean_store_uc'),)
    id = db.Column(db.Integer, primary_key=True)
    ean = db.Column(db.BigInteger, index=True, nullable=False)
    sku = db.Column(db.Integer, index=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    producer = db.Column(db.String(90))
    name = db.Column(db.String(256), nullable=False)
    url = db.Column(db.String(256))
    bula = db.Column(db.String(256))
    description = db.Column(db.Text())
    active_principle = db.Column(db.String(64))
    price = db.Column(db.Numeric(precision=8, scale=2), nullable=False)
    img_small = db.Column(db.String(256))
    promotion_price = db.Column(db.Numeric(precision=8, scale=2))
    promotion_qty = db.Column(db.Integer)
    ms_registry = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, server_default="true",
                          default=True, nullable=False)
    requires_prescription = db.Column(
        db.Boolean, server_default="false", default=False, nullable=False)
    order_items = db.relationship('OrderItems', backref='item', lazy='dynamic')
    timestamp = db.Column(db.DateTime,
                          onupdate=update_timestamp,
                          default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f'<Item {self.ean}>'

    @staticmethod
    def __format_price(price):
        return "R$ {:,.2f}".format(price).replace('.', ',')

    @property
    def buscamed_price(self):
        return self.price * 1

    @property
    def buscamed_formatted_price(self):
        return self.__format_price(self.buscamed_price)

    @property
    def buscamed_promotion_price(self):
        return self.promotion_price * 1

    @property
    def buscamed_formatted_promotion_price(self):
        return self.__format_price(self.buscamed_promotion_price)

    def get_price(self):
        return "R$ {:,.2f}".format(self.price).replace('.', ',')

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': float(self.price),
            'img_small': self.img_small,
            'promotion_price': float(self.promotion_price) if self.promotion_price else None,
            'promotion_qty': self.promotion_qty,
        }

    @classmethod
    def get_best_prices(cls, eans):
        """Best price"""
        subq = db.session.query(cls.ean, func.min(cls.price).label(
            'min_price')).filter(cls.ean.in_(eans)).group_by(cls.ean).subquery()
        subq_2 = db.session.query(cls.ean, func.min(func.least(cls.price, cls.promotion_price)).label(
            'best_price')).filter(cls.ean.in_(eans)).group_by(cls.ean).subquery()
        query = db.session.query(cls, 'best_price').join(subq, and_(
            cls.ean == subq.c.ean, cls.price == subq.c.min_price)).join(subq_2, and_(cls.ean == subq_2.c.ean))
        return query.filter(cls.is_active)

    @classmethod
    def get_ordered_prices_by_id(cls, id):
        """Get ordered prices"""
        item = cls.query.filter_by(id=id).first()
        if item:
            return cls.get_ordered_prices(item.ean)

    @classmethod
    def get_ordered_prices(cls, ean):
        """Get ordered prices"""
        return cls.query.filter_by(ean=ean).order_by(cls.price)

    @classmethod
    def get_list_best_prices(cls, eans, prefix=''):
        """Best prices"""
        subq = db.session.query(cls.ean, func.min(cls.price).label(
            'min_price')).filter(cls.ean.in_(eans)).group_by(cls.ean).subquery()
        query = db.session.query(cls.ean.label(prefix + 'ean'), cls.producer.label(prefix + 'producer'), cls.name.label(prefix + 'name'), cls.url.label(prefix + 'url'),
                                 cls.img_small.label(prefix + 'img_small'), cls.price.label(prefix + 'price'), ).join(subq, and_(cls.ean == subq.c.ean, cls.price == subq.c.min_price))
        return query

    @classmethod
    def get_list_best_promotions(cls, eans, prefix=''):
        """Best promotion"""
        subq = db.session.query(cls.ean, func.min(cls.promotion_price).label(
            'min_promotion_price')).filter(cls.ean.in_(eans)).group_by(cls.ean).subquery()
        query = db.session.query(cls.ean.label(prefix + 'ean'), cls.url.label(prefix + 'url'), cls.promotion_price.label(prefix + 'promotion_price'),
                                 cls.promotion_qty.label(prefix + 'promotion_qty')).join(subq, and_(cls.ean == subq.c.ean, cls.promotion_price == subq.c.min_promotion_price))
        return query

    @classmethod
    def get_list_best_prices_and_promotions(cls, eans):
        """Best price and promotion"""
        # results = Item.get_list_best_prices_and_promotions([7896004710891])
        # Ácido Acetilsalicílico 100 Mg Com 30 Comprimidos Genérico Ems
        prices = cls.get_list_best_prices(eans)

        alias_item_2 = aliased(Item, name='t2')
        subq_promotions = alias_item_2.get_list_best_promotions(
            eans, prefix='p_').subquery()

        results = prices.outerjoin(subq_promotions, and_(
            subq_promotions.columns.p_ean == cls.ean))
        return results


class Permission:
    PRICE = 1
    CREATE = 2
    DELETE = 4
    EDIT = 8
    DELIVERY = 16
    ADMIN = 64  # Buscamed employees only


class PaymentMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    orders = db.relationship('Order', backref='payment_method', lazy='dynamic')

    @staticmethod
    def insert_payments():
        methods = {
            'Dinheiro': Payment.CASH,
            'Cartão de Crédito': Payment.CREDIT_CARD,
            'Cartão de Débito': Payment.DEBIT_CARD,
        }
        for name, id in methods.items():
            payment = PaymentMethod.query.get(id)
            if payment is None:
                payment = PaymentMethod(id=id)
            payment.name = name
            db.session.add(payment)
        db.session.commit()


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self) -> str:
        return f'<Role {self.name}>'

    def __str__(self) -> str:
        return self.name

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    @staticmethod
    def insert_roles():
        roles = {
            'Deliveryman': [Permission.DELIVERY],
            'Moderator': [Permission.PRICE],
            'Owner': [Permission.PRICE, Permission.CREATE, Permission.DELETE, Permission.EDIT],
            'Administrator': [Permission.ADMIN, Permission.PRICE, Permission.DELIVERY],
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            db.session.add(role)
        db.session.commit()


class User(UserMixin, db.Model):
    email_confirmation_key = 'email_confirmation'
    reset_password_key = 'reset_password'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(128), index=True, unique=True, nullable=False)
    confirmed = db.Column(db.Boolean, default=False)

    cep = db.Column(db.Integer)
    logradouro = db.Column(db.String(128))
    bairro = db.Column(db.String(64))
    municipio = db.Column(db.String(64))
    uf = db.Column(db.String(2))
    complemento = db.Column(db.String(64))

    phone = db.Column(db.String(19))
    password_hash = db.Column(db.String(128), nullable=False)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'))
    radius = db.Column(db.Float)
    orders = db.relationship('Order', backref='user', lazy='dynamic')
    detail_clicks = db.relationship(
        'ProductDetailClick', backref='user', lazy='dynamic')
    searches = db.relationship('Searches', backref='user', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None and self.email in current_app.config['ADMINS']:
            self.role = Role.query.filter_by(name='Administrator').first()

    def __repr__(self):
        return f'<User {self.name}>'

    def __str__(self):
        return self.name

    def get_orders(self):
        print(self.orders.all())
        return self.orders

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def generate_auth_token(self, expiration=None):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {self.reset_password_key: self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    def get_email_confirmation_token(self):
        return jwt.encode(
            {self.email_confirmation_key: self.id},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @classmethod
    def verify_reset_password_token(cls, token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])[cls.reset_password_key]
        except:
            return
        return User.query.get(id)

    @classmethod
    def verify_email_confirmation_token(cls, token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])[cls.email_confirmation_key]
        except:
            return
        return User.query.get(id)

    def can(self, permission):
        return self.role is not None and self.role.has_permission(permission)

    @property
    def is_admin(self):
        return self.can(Permission.ADMIN)

    @property
    def is_deliveryman(self):
        return self.can(Permission.DELIVERY)


class FarmaSeguraWaitLine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    phone = db.Column(db.String(19), unique=True, nullable=True)


class AnonymousUser(AnonymousUserMixin):
    store_id = None

    def can(self, permission):
        return False

    @property
    def is_admin(self):
        return False


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


login_manager.anonymous_user = AnonymousUser
