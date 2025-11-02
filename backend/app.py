from flask import Flask, request, make_response, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager, create_access_token
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# Simple config
class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///vendorsync.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'your-secret-key'

# Simple resources
from flask_restful import Resource

class Login(Resource):
    def post(self):
        from flask import request
        data = request.get_json()
        
        demo_users = {
            'admin@vendorsync.com': {'password': 'admin123', 'role': 'manager', 'name': 'Admin User'},
            'vendor@example.com': {'password': 'vendor123', 'role': 'vendor', 'name': 'Vendor User'},
            'client@example.com': {'password': 'client123', 'role': 'client', 'name': 'Client User'}
        }
        
        if not data or not data.get('email') or not data.get('password'):
            return {'message': 'Email and password are required'}, 400
        
        email = data['email'].lower()
        password = data['password']
        
        if email not in demo_users or demo_users[email]['password'] != password:
            return {'message': 'Invalid email or password'}, 401
        
        user = demo_users[email]
        token = create_access_token(identity=email)
        
        return {
            'token': token,
            'user': {
                'id': 1,
                'email': email,
                'role': user['role'],
                'name': user['name'],
                'first_name': user['name'].split()[0],
                'last_name': user['name'].split()[1]
            }
        }, 200

class UserResource(Resource):
    def get(self):
        return {'message': 'User endpoint'}, 200
    def post(self):
        return {'message': 'User created successfully'}, 201

class Dashboard(Resource):
    def get(self):
        return {'message': 'Dashboard endpoint'}, 200

class OrderResource(Resource):
    def get(self, id=None):
        return {'message': 'Orders'}, 200
    def post(self):
        return {'message': 'Order created'}, 201

class OrderVendorResource(Resource):
    def get(self):
        return {'message': 'Vendor orders'}, 200

class OrderAssignmentResource(Resource):
    def get(self, assignment_id=None):
        return {'message': 'Assignments'}, 200

class QuoteResource(Resource):
    def get(self, id=None):
        return {'message': 'Quotes'}, 200

class DocumentResource(Resource):
    def get(self):
        return {'message': 'Documents'}, 200

class SearchResource(Resource):
    def get(self):
        return {'message': 'Search'}, 200

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
jwt = JWTManager(app)

# Configure CORS with more permissive settings for development
app.config['CORS_HEADERS'] = 'Content-Type, Authorization'
app.config['CORS_SUPPORTS_CREDENTIALS'] = True
app.config['CORS_ORIGINS'] = '*'  # Allow all origins in development

# Initialize CORS with more permissive settings
cors = CORS(
    app,
    resources={
        r"/*": {
            "origins": "*",  # Allow all origins
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
            "allow_headers": ["*"],  # Allow all headers
            "expose_headers": ["Content-Range", "X-Content-Range", "Authorization"],
            "supports_credentials": True,
            "max_age": 600  # 10 minutes
        }
    }
)

# Handle preflight requests
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "*")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Max-Age', '600')
    return response

# Simple models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

# Add your endpoints
api.add_resource(Login, '/auth/login')
api.add_resource(UserResource, '/users')
api.add_resource(Dashboard, '/dashboard')
api.add_resource(OrderResource, '/orders', '/orders/<int:id>')  # Your endpoints
api.add_resource(OrderVendorResource, '/orders/vendor')  # Your endpoint
api.add_resource(OrderAssignmentResource, '/order-assignments', '/order-assignments/<int:assignment_id>')  # Your endpoint
api.add_resource(QuoteResource, '/quotes', '/quotes/<int:id>')
api.add_resource(DocumentResource, '/documents')
api.add_resource(SearchResource, '/search')

@jwt.unauthorized_loader
def missing_token_callback(error):
    return {'message': 'Access token is missing'}, 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return {'message': 'Invalid access token'}, 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return {'message': 'Access token has expired'}, 401

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)