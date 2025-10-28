from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from backend.models.user import User
from backend.models.role import Role
from backend import db

class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True, help="Email is required")
        parser.add_argument('password', required=True, help="Password is required")
        args = parser.parse_args()

        user = User.query.filter_by(email=args['email']).first()
        if not user or not check_password_hash(user.password_hash, args['password']):
            return {'message': 'Invalid credentials'}, 401

        token = create_access_token(identity=user.id)

        return {
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role.name
            }
        }, 200

class Register(Resource):
    @jwt_required()
    def post(self):
        current_user = User.query.get(get_jwt_identity())

        if not current_user or current_user.role.name.lower() != 'manager':
            return {'message': 'Unauthorized – only managers can create users'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True, help="Email is required")
        parser.add_argument('password', required=True, help="Password is required")
        parser.add_argument('first_name', required=True, help="First name is required")
        parser.add_argument('last_name', required=True, help="Last name is required")
        parser.add_argument('phone', required=False)
        parser.add_argument('role_id', type=int, required=True, help="Role ID is required")
        args = parser.parse_args()

        if User.query.filter_by(email=args['email']).first():
            return {'message': 'Email already exists'}, 400

        role = Role.query.get(args['role_id'])
        if not role:
            return {'message': 'Invalid role'}, 400

        user = User(
            email=args['email'],
            password_hash=generate_password_hash(args['password']),
            first_name=args['first_name'],
            last_name=args['last_name'],
            phone=args.get('phone'),
            role_id=args['role_id'],
            is_active=True
        )

        db.session.add(user)
        db.session.commit()

        return {'message': 'User registered successfully'}, 201
