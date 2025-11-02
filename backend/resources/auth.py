from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash

class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help='Email is required')
        parser.add_argument('password', type=str, required=True, help='Password is required')
        data = parser.parse_args()
        
        # Demo users for testing
        demo_users = {
            'admin@vendorsync.com': {'password': 'admin123', 'role': 'manager', 'name': 'Admin User'},
            'vendor@example.com': {'password': 'vendor123', 'role': 'vendor', 'name': 'Vendor User'},
            'client@example.com': {'password': 'client123', 'role': 'client', 'name': 'Client User'}
        }
        
        email = data['email'].lower()
        password = data['password']
        
        if email not in demo_users or demo_users[email]['password'] != password:
            return {'message': 'Invalid email or password'}, 401
        
        user = demo_users[email]
        access_token = create_access_token(identity=email)
        
        return {
            'token': access_token,
            'user': {
                'id': 1,
                'email': email,
                'role': user['role'],
                'name': user['name'],
                'first_name': user['name'].split()[0],
                'last_name': user['name'].split()[1]
            }
        }, 200
