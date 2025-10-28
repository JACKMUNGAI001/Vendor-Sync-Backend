from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_cors import CORS

# Import your resources
from resources.auth import Login
from resources.user import UserResource
from resources.dashboard import Dashboard
from resources.order import OrderResource, OrderVendorResource, OrderAssignmentResource  # Add these
from resources.quote import QuoteResource
from resources.document import DocumentResource
from resources.search import SearchResource
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
jwt = JWTManager(app)
CORS(app)  # Enable CORS for frontend

# Import models (important for db.create_all())
from models.role import Role
from models.user import User
from models.vendor import Vendor
from models.purchase_order import PurchaseOrder  # Add this
from models.quote import Quote
from models.document import Document
from models.order_assignment import OrderAssignment  # Add this

# Add your endpoints
api.add_resource(Login, '/login')
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