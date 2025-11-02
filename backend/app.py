from flask import Flask, request, make_response
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from backend.database import db

# Import your resources
from backend.resources.auth import Login
from backend.resources.user import UserResource
from backend.resources.dashboard import Dashboard
from backend.resources.order import OrderResource, OrderVendorResource, OrderAssignmentResource  # Add these
from backend.resources.quote import QuoteResource
from backend.resources.document import DocumentResource
from backend.resources.search import SearchResource
from backend.config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
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

# Import models (important for db.create_all())
from backend.models.role import Role
from backend.models.user import User
from backend.models.vendor import Vendor
from backend.models.purchase_order import PurchaseOrder  # Add this
from backend.models.quote import Quote
from backend.models.document import Document
from backend.models.order_assignment import OrderAssignment  # Add this

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