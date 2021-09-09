from flask import Blueprint, g
from flask_restful import Api
from flask_httpauth import HTTPBasicAuth
from app.models import User


authentication = HTTPBasicAuth()


@authentication.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        return False
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token) 
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.check_password(password)



bp = Blueprint('api', __name__)
rest_api = Api(bp)


from app.api import autocomplete, auth, main, order, user, farmasegura
