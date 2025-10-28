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
        if User.query.get(get_jwt_identity()).role.name != 'manager':
            return {'message': 'Unauthorized'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True)
        parser.add_argument('password', required=True)
        parser.add_argument('role_id', type=int, required=True)
        args = parser.parse_args()

        if User.query.filter_by(email=args['email']).first():
            return {'message': 'Email already exists'}, 400

        if not Role.query.get(args['role_id']):
            return {'message': 'Invalid role'}, 400

        user = User(
            email=args['email'],
            password_hash=hashlib.sha256(args['password'].encode()).hexdigest(),
            role_id=args['role_id']
        )
        db.session.add(user)
        db.session.commit()
        return {'message': 'User registered successfully'}, 201