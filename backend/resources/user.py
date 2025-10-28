from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from backend.models.user import User
from backend.models.role import Role
from backend.app import db


class UserResource(Resource):
    @jwt_required()
    def post(self):
        """Create a new user (only accessible by manager)."""
        current_user = User.query.get(get_jwt_identity())
        if not current_user or current_user.role.name != 'manager':
            return {'message': 'Unauthorized'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True, help="Email is required")
        parser.add_argument('password', required=True, help="Password is required")
        parser.add_argument('role_id', type=int, required=True, help="Role ID is required")
        args = parser.parse_args()

        if User.query.filter_by(email=args['email']).first():
            return {'message': 'Email already exists'}, 400

        if not Role.query.get(args['role_id']):
            return {'message': 'Invalid role'}, 400

        new_user = User(
            email=args['email'],
            password_hash=generate_password_hash(args['password']),
            role_id=args['role_id']
        )
        db.session.add(new_user)
        db.session.commit()

        return {'message': 'User created successfully'}, 201

    @jwt_required()
    def delete(self):
        """Delete an existing user (only accessible by manager)."""
        current_user = User.query.get(get_jwt_identity())
        if not current_user or current_user.role.name != 'manager':
            return {'message': 'Unauthorized'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True, help="User ID is required")
        args = parser.parse_args()

        user_to_delete = User.query.get(args['user_id'])
        if not user_to_delete:
            return {'message': 'User not found'}, 404

        db.session.delete(user_to_delete)
        db.session.commit()

        return {'message': 'User deleted successfully'}, 200
