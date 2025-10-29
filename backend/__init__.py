from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from backend.config import Config

db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/*": {"origins": ["https://relaxed-rolypoly-176184.netlify.app"]}})

    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)

    from backend.models import role, user, vendor, purchase_order, quote, document, order_assignment
    from backend.resources.auth import Login, Register
    from backend.resources.user import UserResource
    from backend.resources.dashboard import Dashboard
    from backend.resources.order import OrderResource, OrderVendorResource, OrderAssignmentResource
    from backend.resources.quote import QuoteResource
    from backend.resources.document import DocumentResource
    from backend.resources.search import SearchResource

    api = Api(app)

    api.add_resource(Login, '/login')
    api.add_resource(Register, '/register')
    api.add_resource(UserResource, '/users')
    api.add_resource(Dashboard, '/dashboard')
    api.add_resource(OrderResource, '/orders', '/orders/<int:id>')
    api.add_resource(OrderVendorResource, '/orders/vendor')
    api.add_resource(OrderAssignmentResource,
                     '/order-assignments',
                     '/order-assignments/<int:assignment_id>')
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

    @app.route('/')
    def index():
        return "Vendor Sync Backend is running!"

    print("Flask app fully ready with bound API routes")
    return app
