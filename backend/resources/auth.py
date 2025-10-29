from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token
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
        if not user:
            return {'message': 'Invalid email or password'}, 401

        if not check_password_hash(user.password_hash, args['password']):
            return {'message': 'Invalid email or password'}, 401

        if not user.is_active:
            return {'message': 'Account is deactivated'}, 401

        token = create_access_token(identity=user.id)
        return {
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role.name if user.role else 'unknown'
            }
        }, 200

class Register(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True, help="Email is required")
        parser.add_argument('password', required=True, help="Password is required")
        parser.add_argument('first_name', required=True, help="First name is required")
        parser.add_argument('last_name', required=True, help="Last name is required")
        parser.add_argument('phone', required=False)
        parser.add_argument('company_name', required=False)
        args = parser.parse_args()

        if User.query.filter_by(email=args['email']).first():
            return {'message': 'Email already exists'}, 400

        vendor_role = Role.query.filter_by(name='vendor').first()
        if not vendor_role:
            vendor_role = Role(name='vendor')
            db.session.add(vendor_role)
            db.session.commit()

        user = User(
            email=args['email'],
            password_hash=generate_password_hash(args['password']),
            first_name=args['first_name'],
            last_name=args['last_name'],
            phone=args.get('phone'),
            role_id=vendor_role.id,
            is_active=True
        )

        try:
            db.session.add(user)
            db.session.commit()
            
            token = create_access_token(identity=user.id)
            return {
                'message': 'User registered successfully',
                'token': token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': 'vendor'
                }
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {'message': f'Registration failed: {str(e)}'}, 500