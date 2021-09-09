from app.api import rest_api
from flask_restful import Resource, reqparse, fields, marshal_with
from app.models import Item
from flask import current_app


product_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'img_small': fields.String,
    'active_principle': fields.String,
    'producer': fields.String,
    'store': fields.String,
    'price': fields.Float,
    'promotion_price': fields.Float,
    'promotion_qty': fields.Integer,
    'own_delivery': fields.Boolean,
    'buscamed_delivery': fields.Boolean,
}


class Product(Resource):
    @marshal_with(product_fields)
    def get(id):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'id', type=int, help='Provide a product id', required=True)
        args = parser.parse_args(strict=True)
        item = Item.query.get(args['id'])
        return item


detail_fields = {
    'name': fields.String,
    'img_small': fields.String,
    'prices': fields.List(
        fields.Nested({
            'name': fields.String,
            'url': fields.String,
            'bula': fields.String,
            'store': fields.String,
            'price': fields.Float,
            'promotion_price': fields.Float,
            'promotion_qty': fields.Integer,
            'description': fields.String,
            'active_principle': fields.String,
            'producer': fields.String,
            'own_delivery': fields.Boolean,
            'buscamed_delivery': fields.Boolean,
        })
    )
}


class Detail(Resource):
    @marshal_with(detail_fields)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'id', type=int, help='Provide a product id', required=True)
        args = parser.parse_args(strict=True)
        items = Item.get_ordered_prices_by_id(args['id'])
        response = dict(img_small=items[0].img_small, prices=list(),
                        name=items[0].name, producer=items[0].producer)
        for item in items:
            response['prices'].append(
                {
                    'name': item.name,
                    'url': item.url,
                    'bula': item.bula,
                    'store': item.store.name,
                    'price': item.price,
                    'promotion_price': item.promotion_price,
                    'promotion_qty': item.promotion_qty,
                    'description': item.description,
                    'active_principle': item.active_principle,
                    'producer': item.producer,
                    'own_delivery': item.store.own_delivery,
                    'buscamed_delivery': item.store.buscamed_delivery,
                }
            )
        return response


search_fields = {
    'page': fields.Integer,
    'total': fields.Integer,
    'items': fields.List(
        fields.Nested(
            {
                'id': fields.Integer,
                'name': fields.String,
                'img_small': fields.String,
                'best_price': fields.Float,
                'producer': fields.String,
                'active_principle': fields.String,
            }
        )
    )
}


class Index(Resource):
    @marshal_with(search_fields)
    def get(self, **kwargs):
        eans = [
            7896004710891,
            7896023703010,
            891142203014,
            7896422509589,
            7896116860217,
            7896658035388,
            7898569765071,
            7891106914369,
            7896422524452,
            7896422526975,
            7896714211275,
            7891045043588,
            7896015518875,
        ]
        items = Item.get_best_prices(eans)
        return formatter(items, len(eans))


class Search(Resource):
    @marshal_with(search_fields)
    def get(self, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'q', type=str, help='Provide a string for searching', required=True)
        parser.add_argument('page', type=int, default=1,
                            help='Provide a page')
        args = parser.parse_args(strict=True)
        items, total = Item.search(
            args['q'], args['page'], current_app.config['ITEMS_PER_PAGE'])
        return formatter(items, total, args['page'])


def formatter(items, total, page=1):
    response = dict(items=list(), total=total, page=page)
    for item, best_price in items:
        if item is None:
            continue
        response['items'].append(
            {
                'id': item.id,
                'name': item.name,
                'img_small': item.img_small,
                'best_price': best_price,
                'producer': item.producer,
                'active_principle': item.active_principle,
            }
        )
    return response


rest_api.add_resource(Search, '/search')
rest_api.add_resource(Detail, '/detail')
rest_api.add_resource(Product, '/product')
rest_api.add_resource(Index, '/index')
