from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token
from backend.models.user import User
from werkzeug.security import check_password_hash

class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help='Email is required')
        parser.add_argument('password', type=str, required=True, help='Password is required')
        data = parser.parse_args()
        
        # Find user by email
        user = User.query.filter_by(email=data['email'].lower()).first()
        
        if not user:
            return {'message': 'Invalid email or password'}, 401
            
        # Verify password
        if not check_password_hash(user.password_hash, data['password']):
            return {'message': 'Invalid email or password'}, 401
            
        # Create token
        access_token = create_access_token(identity=user.id)
        
        # Map role names to expected format
        role_mapping = {
            'ADMIN': 'manager',
            'VENDOR': 'vendor', 
            'CLIENT': 'client'
        }
        
        return {
            'token': access_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'role': role_mapping.get(user.role.name, user.role.name.lower()),
                'name': f"{user.first_name} {user.last_name}",
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        }, 200
