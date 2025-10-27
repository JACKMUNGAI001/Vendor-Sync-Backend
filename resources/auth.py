from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from models.user import User
from models.role import Role
from app import db
import hashlib

class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True)
        parser.add_argument('password', required=True)
        args = parser.parse_args()

        user = User.query.filter_by(email=args['email']).first()
        if not user or hashlib.sha256(args['password'].encode()).hexdigest() != user.password_hash:
            return {'message': 'Invalid credentials'}, 401

        token = create_access_token(identity=user.id)
        return {'token': token, 'role': user.role.name}, 200

class Register(Resource):
    @jwt_required()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True)
        parser.add_argument('password', required=True)
        parser.add_argument('role_id', type=int, required=True)
        args = parser.parse_args()

        return {'message': 'Register endpoint setup'}, 201