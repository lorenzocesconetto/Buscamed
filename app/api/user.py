from flask import g
from app.api import rest_api, authentication
from flask_restful import Resource, fields, marshal_with, reqparse
from app.models import User
from app import db
from app.api.errors import unauthorized


user_fields = {
    'name': fields.String,
    'email': fields.String,
    'cep': fields.Integer,
    'logradouro': fields.String,
    'complemento': fields.String,
    'bairro': fields.String,
    'municipio': fields.String,
    'uf': fields.String,
    'phone': fields.String,
    'confirmed': fields.Boolean,
    'radius': fields.Float,
}


class User(Resource):
    @authentication.login_required
    @marshal_with(user_fields)
    def get(self):
        if g.current_user.is_anonymous:
            return unauthorized('Invalid credentials')
        return g.current_user

    @authentication.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'name', type=str, help='Provide a valid name', required=True)
        parser.add_argument(
            'cep', type=int, help='Provide a valid cep', required=True)
        parser.add_argument('logradouro', type=str,
                            help='Provide a valid logradouro', required=True)
        parser.add_argument('complemento', type=str,
                            help='Provide a valid complemento', required=True)
        parser.add_argument('bairro', type=str,
                            help='Provide a valid bairro', required=True)
        parser.add_argument('municipio', type=str,
                            help='Provide a valid municipio', required=True)
        parser.add_argument(
            'uf', type=str, help='Provide a valid uf', required=True)
        parser.add_argument('phone', type=str,
                            help='Provide a valid phone', required=True)
        parser.add_argument('radius', type=float,
                            help='Provide a valid radius')
        args = parser.parse_args(strict=True)
        for key in args.keys():
            setattr(g.current_user, key, args[key])
        db.session.commit()
        return {'message': 'Usuario alterado com sucesso'}, 200


rest_api.add_resource(User, '/user')
