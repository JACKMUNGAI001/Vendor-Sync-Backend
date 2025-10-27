from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.role import Role
from app import db
import hashlib

class UserResource(Resource):
    @jwt_required()
    def post(self):
        if User.query.get(get_jwt_identity()).role.name != 'manager':
            return {'message': 'Unauthorized'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True)
        parser.add_argument('password', required=True)
        parser.add_argument('role_id', type=int, required=True)
        args = parser.parse_args()

        if not Role.query.get(args['role_id']):
            return {'message': 'Invalid role'}, 400

        user = User(
            email=args['email'],
            password_hash=hashlib.sha256(args['password'].encode()).hexdigest(),
            role_id=args['role_id']
        )
        db.session.add(user)
        db.session.commit()
        return {'message': 'User created'}, 201

    @jwt_required()
    def delete(self):
        if User.query.get(get_jwt_identity()).role.name != 'manager':
            return {'message': 'Unauthorized'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True)
        args = parser.parse_args()

        user = User.query.get(args['user_id'])
        if not user:
            return {'message': 'User not found'}, 404

        db.session.delete(user)
        db.session.commit()
        return {'message': 'User deleted'}, 200