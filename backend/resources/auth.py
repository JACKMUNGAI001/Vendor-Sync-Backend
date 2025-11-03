from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from backend.models.user import User
from backend.models.role import Role
from backend.models.vendor import Vendor
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
        
        if not user.check_password(args['password']):
            return {'message': 'Invalid email or password'}, 401
        
        if not user.is_active:
            return {'message': 'Account is inactive. Please contact administrator.'}, 403

        token = create_access_token(identity=str(user.id))
        
        return {
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role.name,
                'role_id': user.role_id
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
        parser.add_argument('role', required=True, help="Role is required")
        parser.add_argument('company_name', required=False)
        parser.add_argument('address', required=False)
        parser.add_argument('contact_person', required=False)
        args = parser.parse_args()

        if User.query.filter_by(email=args['email']).first():
            return {'message': 'Email already exists'}, 400

        role_name = args['role'].lower()
        if role_name not in ['manager', 'staff', 'vendor']:
            return {'message': 'Invalid role. Must be manager, staff, or vendor'}, 400

        role = Role.query.filter_by(name=role_name).first()
        if not role:
            return {'message': f'{role_name.capitalize()} role not found. Please contact administrator.'}, 500

        user = User(
            email=args['email'],
            password_hash=generate_password_hash(args['password']),
            first_name=args['first_name'],
            last_name=args['last_name'],
            phone=args.get('phone'),
            role_id=role.id,
            is_active=True
        )

        try:
            db.session.add(user)
            db.session.flush()

            if role_name == 'vendor':
                vendor = Vendor(
                    name=f"{args['first_name']} {args['last_name']}",
                    email=args['email'],
                    phone=args.get('phone'),
                    address=args.get('address'),
                    company_name=args.get('company_name', f"{args['first_name']} {args['last_name']} Co."),
                    contact_person=args.get('contact_person', f"{args['first_name']} {args['last_name']}"),
                    is_verified=False
                )
                db.session.add(vendor)
            
            db.session.commit()
            
            token = create_access_token(identity=str(user.id))
            
            message = 'Registration successful'
            if role_name == 'vendor':
                message = 'Vendor registered successfully. Awaiting manager approval.'
            
            return {
                'message': message,
                'token': token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role.name,
                    'role_id': user.role_id,
                    'is_verified': False if role_name == 'vendor' else True
                }
            }, 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Registration failed: {str(e)}'}, 500