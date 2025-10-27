from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from app import db
import hashlib

class UserResource(Resource):
    @jwt_required()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True)
        parser.add_argument('password', required=True)
        parser.add_argument('role_id', type=int, required=True)
        args = parser.parse_args()

        user = User(
            email=args['email'],
            password_hash=hashlib.sha256(args['password'].encode()).hexdigest(),
            role_id=args['role_id']
        )
        db.session.add(user)
        db.session.commit()
        return {'message': 'User created'}, 201