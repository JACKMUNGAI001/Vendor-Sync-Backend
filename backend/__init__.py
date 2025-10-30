from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from backend.config import Config

db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(
        app,
        resources={r"/api/*": {"origins": "https://wondrous-twilight-609097.netlify.app"}},
        supports_credentials=True
    )

    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    from backend.resources.auth import Login, Register
    from backend.resources.user import UserResource
    from backend.resources.dashboard import Dashboard
    from backend.resources.order import (
        OrderResource,
        OrderVendorResource,
        OrderAssignmentResource,
    )
    from backend.resources.quote import QuoteResource
    from backend.resources.document import DocumentResource
    from backend.resources.search import SearchResource
    from backend.resources.vendor import VendorResource

    api = Api(app)

    api.add_resource(Login, "/api/login")
    api.add_resource(Register, "/api/register")
    api.add_resource(UserResource, "/api/users")
    api.add_resource(Dashboard, "/api/dashboard")
    api.add_resource(OrderResource, "/api/orders", "/api/orders/<int:id>")
    api.add_resource(OrderVendorResource, "/api/orders/vendor")
    api.add_resource(
        OrderAssignmentResource,
        "/api/order-assignments",
        "/api/order-assignments/<int:assignment_id>",
    )
    api.add_resource(QuoteResource, "/api/quotes", "/api/quotes/<int:id>")
    api.add_resource(DocumentResource, "/api/documents")
    api.add_resource(SearchResource, "/api/search")
    api.add_resource(VendorResource, "/api/vendors")

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {"message": "Access token is missing"}, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {"message": "Invalid access token"}, 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {"message": "Access token has expired"}, 401

    @app.route("/")
    def index():
        return "Vendor Sync Backend is running!"

    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "ok",
            "message": "Backend running successfully"
        }), 200

    return app
