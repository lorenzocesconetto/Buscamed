from flask import g
from app.api import rest_api, authentication
from flask_restful import Resource, reqparse, fields, marshal_with
from app.checkers import check_email, check_email_unique, check_phone, exact_length, min_length
from app.models import User
from app import db
from app.auth.email import send_password_reset_email, send_email_confirmation_email
from app.api.errors import unauthorized


class Login(Resource):
    @authentication.login_required
    def get(self):
        if g.current_user.is_anonymous or g.token_used:
            return unauthorized('Invalid credentials')
        return {'token': g.current_user.generate_auth_token(), 'expiration': None}


class Register(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'name', type=str, help='Provide a valid name', required=True)
        parser.add_argument('email', type=check_email,
                            help='Provide a valid account email', required=True)
        parser.add_argument(
            'cep', type=int, help='Numbers only', required=True)
        parser.add_argument('logradouro', type=str,
                            help='Provide a valid logradouro', required=True)
        parser.add_argument('complemento', type=str,
                            help='Provide a valid complemento', required=True)
        parser.add_argument('bairro', type=str,
                            help='Provide a valid bairro', required=True)
        parser.add_argument('municipio', type=str,
                            help='Provide a valid cidade', required=True)
        parser.add_argument(
            'uf', type=exact_length(2), help='Provide a valid uf', required=True)
        parser.add_argument('phone', type=check_phone,
                            help='Provide numbers only for phone', required=True)
        parser.add_argument('password', type=min_length(
            7), help='Provide the account password', required=True)
        args = parser.parse_args(strict=True)
        user = User.query.filter_by(email=args['email']).first()
        if user:
            return {
                'message': {
                    "email": "Email já cadastrado na plataforma"
                }}, 400
        user = User(
            name=args['name'],
            email=args['email'],
            cep=args['cep'],
            logradouro=args['logradouro'],
            complemento=args['complemento'],
            bairro=args['bairro'],
            municipio=args['municipio'],
            uf=args['uf'],
            phone=args['phone'],
        )
        user.set_password(args['password'])
        db.session.add(user)
        db.session.commit()
        send_email_confirmation_email(user)
        return {'success': True, 'token': user.generate_auth_token(), 'expiration': None}, 200


class ForgotPassword(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=check_email,
                            help='Provide a valid account email', required=True)
        args = parser.parse_args(strict=True)
        user = User.query.filter_by(email=args['email']).first()
        if user:
            send_password_reset_email(user)
        return {'success': True}, 200


rest_api.add_resource(Login, '/token')
rest_api.add_resource(Register, '/register')
rest_api.add_resource(ForgotPassword, '/forgot_password')
