from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from backend.config import Config
# from backend.services.cloudinary_service import cloudinary_service # Temporarily commented out
# from backend.services.email_service import EmailService # Temporarily commented out
# from backend.services.algolia_service import AlgoliaService # Temporarily commented out

db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()
migrate = Migrate()
# cloudinary_service = CloudinaryService() # Temporarily commented out

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Initialize email_service after app is configured # Temporarily commented out
    # app.email_service = EmailService() # Temporarily commented out

    # Initialize algolia_service after app is configured # Temporarily commented out
    # app.algolia_service = AlgoliaService() # Temporarily commented out

    from backend.resources.auth import Login, Register
    from backend.resources.dashboard import Dashboard
    from backend.resources.document import DocumentResource
    from backend.resources.order import OrderResource, OrderAssignmentResource, OrderVendorResource
    from backend.resources.quote import QuoteResource
    from backend.resources.search import SearchResource
    from backend.resources.user import UserResource
    from backend.resources.vendor import VendorResource
    from backend.resources.requirement import RequirementResource
    from backend.resources.vendor_category import VendorCategoryResource
    from backend.resources.role import RoleResource

    api = Api(app)

    api.add_resource(Login, "/api/login")
    api.add_resource(Register, "/api/register")
    api.add_resource(Dashboard, "/api/dashboard")
    api.add_resource(DocumentResource, "/api/documents")
    api.add_resource(OrderResource, "/api/orders", "/api/orders/<int:id>")
    api.add_resource(OrderAssignmentResource, "/api/order-assignments", "/api/order-assignments/<int:assignment_id>")
    api.add_resource(OrderVendorResource, "/api/vendor-orders")
    api.add_resource(QuoteResource, "/api/quotes", "/api/quotes/<int:id>")
    api.add_resource(SearchResource, "/api/search")
    api.add_resource(UserResource, "/api/users", "/api/users/<int:id>")
    api.add_resource(VendorResource, "/api/vendors", "/api/vendors/<int:id>")
    api.add_resource(RequirementResource, "/api/requirements", "/api/requirements/<int:id>")
    api.add_resource(VendorCategoryResource, "/api/vendor-categories", "/api/vendor-categories/<int:id>")
    api.add_resource(RoleResource, "/api/roles")

    @app.route("/")
    def index():
        return "Vendor Sync Backend is running!"

    @app.route("/api/health")
    def health_check():
        return jsonify({"status": "ok", "message": "Backend running successfully"}), 200

    from backend.db_seed import seed_roles, seed_users, seed_vendors

    class SeedDB(Resource):
        def get(self):
            seed_roles()
            seed_users()
            seed_vendors()
            return {"message": "Database seeded successfully"}, 200

    api.add_resource(SeedDB, "/api/seed-db")

    return app