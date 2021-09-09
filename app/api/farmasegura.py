from app.telegram import telegram_message
from app.checkers import min_length
from app.models import FarmaSeguraWaitLine
from app.api import rest_api
from flask_restful import Resource, reqparse
from app import db


class WaitLine(Resource):
    def post(id):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'name', type=min_length(1), help='Provide valid name', required=True)
        parser.add_argument(
            'email', type=min_length(1), help='Provide valid email', required=True)
        parser.add_argument(
            'phone', type=min_length(1), help='Provide a valid phone', required=False)
        args = parser.parse_args(strict=True)
        
        # Send telegram
        # telegram_message(f'{args["name"]} - {args["email"]}')
        
        obj = FarmaSeguraWaitLine(
            name=args['name'], email=args['email'], phone=args['phone'])
        db.session.add(obj)
        db.session.commit()
        return {'message': 'success'}, 200


rest_api.add_resource(WaitLine, '/wait_line')
