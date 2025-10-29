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

    CORS(app, resources={
        r"/*": {
            "origins": [
                "https://wondrous-twilight-609097.netlify.app",
                "http://localhost:3000",
                "http://127.0.0.1:3000"
            ],
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })

    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)

    from backend.resources.auth import Login, Register
    from backend.resources.dashboard import Dashboard
    from backend.resources.order import OrderResource
    from backend.resources.vendor import VendorResource

    api = Api(app)

    api.add_resource(Login, '/login')
    api.add_resource(Register, '/register')
    api.add_resource(Dashboard, '/dashboard')
    api.add_resource(OrderResource, '/orders', '/orders/<int:id>')
    api.add_resource(VendorResource, '/vendors')

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
        return {
            'message': 'VendorSync Backend is running!',
            'endpoints': {
                'login': '/login',
                'register': '/register',
                'dashboard': '/dashboard',
                'orders': '/orders',
                'vendors': '/vendors'
            }
        }

    return app