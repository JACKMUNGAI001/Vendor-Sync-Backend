from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from backend.models.user import User
from backend.models.role import Role
from backend import db

class UserResource(Resource):
    @jwt_required()
    def get(self, id=None):
        current_user = User.query.get(get_jwt_identity())
        if not current_user or current_user.role.name != 'manager':
            return {'message': 'Unauthorized'}, 403

        if id:
            user = User.query.get(id)
            if not user:
                return {'message': 'User not found'}, 404
            return user.to_dict(), 200

        users = User.query.all()
        return {'users': [user.to_dict() for user in users]}, 200

    @jwt_required()
    def post(self):
        current_user = User.query.get(get_jwt_identity())
        if not current_user or current_user.role.name != 'manager':
            return {'message': 'Unauthorized'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True, help="Email is required")
        parser.add_argument('password', required=True, help="Password is required")
        parser.add_argument('first_name', required=True, help="First name is required")
        parser.add_argument('last_name', required=True, help="Last name is required")
        parser.add_argument('phone', type=str)
        parser.add_argument('role_id', type=int, required=True, help="Role ID is required")
        args = parser.parse_args()

        if User.query.filter_by(email=args['email']).first():
            return {'message': 'Email already exists'}, 400

        if not Role.query.get(args['role_id']):
            return {'message': 'Invalid role'}, 400

        new_user = User(
            email=args['email'],
            password_hash=generate_password_hash(args['password']),
            first_name=args['first_name'],
            last_name=args['last_name'],
            phone=args['phone'],
            role_id=args['role_id']
        )
        db.session.add(new_user)
        db.session.commit()

        return {'message': 'User created successfully', 'user': new_user.to_dict()}, 201

    @jwt_required()
    def patch(self, id):
        current_user = User.query.get(get_jwt_identity())
        if not current_user or current_user.role.name != 'manager':
            return {'message': 'Unauthorized'}, 403

        user_to_update = User.query.get(id)
        if not user_to_update:
            return {'message': 'User not found'}, 404

        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str)
        parser.add_argument('first_name', type=str)
        parser.add_argument('last_name', type=str)
        parser.add_argument('phone', type=str)
        parser.add_argument('role_id', type=int)
        args = parser.parse_args()

        if args['email'] and args['email'] != user_to_update.email:
            if User.query.filter_by(email=args['email']).first():
                return {'message': 'Email already exists'}, 400
            user_to_update.email = args['email']
        
        if args['first_name']:
            user_to_update.first_name = args['first_name']
        if args['last_name']:
            user_to_update.last_name = args['last_name']
        if args['phone']:
            user_to_update.phone = args['phone']
        if args['role_id']:
            if not Role.query.get(args['role_id']):
                return {'message': 'Invalid role'}, 400
            user_to_update.role_id = args['role_id']

        db.session.commit()

        return {'message': 'User updated successfully', 'user': user_to_update.to_dict()}, 200

    @jwt_required()
    def delete(self, id):
        current_user = User.query.get(get_jwt_identity())
        if not current_user or current_user.role.name != 'manager':
            return {'message': 'Unauthorized'}, 403

        user_to_delete = User.query.get(id)
        if not user_to_delete:
            return {'message': 'User not found'}, 404

        db.session.delete(user_to_delete)
        db.session.commit()

        return {'message': 'User deleted successfully'}, 200


class CheckUserRole(Resource):
    def get(self, user_id):
        query = """
            SELECT users.id, users.username, roles.name AS role_name, roles.id AS role_id
            FROM users
            JOIN roles ON users.role_id = roles.id
            WHERE users.id = :user_id
        """
        result = db.session.execute(query, {'user_id': user_id}).fetchone()

        if result:
            return {
                'user_id': result.id,
                'username': result.username,
                'role_name': result.role_name,
                'role_id': result.role_id
            }, 200
        else:
            return {'message': 'User not found'}, 404
