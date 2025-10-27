from flask_restful import Resource, reqparse
from models.user import User
import hashlib

class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True)
        parser.add_argument('password', required=True)
        args = parser.parse_args()

        user = User.query.filter_by(email=args['email']).first()
        if not user:
            return {'message': 'Invalid credentials'}, 401

        return {'message': 'Login endpoint setup'}, 200