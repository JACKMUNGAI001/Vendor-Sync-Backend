from dotenv import load_dotenv
load_dotenv()
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
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

    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    from backend.models import (
        User, Vendor, Role, Requirement, VendorCategory,
        PurchaseOrder, OrderAssignment, Document, Quote
    )

    from backend.resources.auth import Login, Register
    from backend.resources.dashboard import Dashboard
    from backend.resources.document import DocumentResource
    from backend.resources.order import OrderResource, OrderAssignmentResource, OrderVendorResource
    from backend.resources.quote import QuoteResource
    from backend.resources.search import SearchResource
    from backend.resources.user import UserResource, CheckUserRole
    from backend.resources.vendor import VendorResource
    from backend.resources.requirement import RequirementResource
    from backend.resources.vendor_category import VendorCategoryResource
    from backend.resources.role import RoleResource

    api = Api(app)

    api.add_resource(Login, "/api/login")
    api.add_resource(Register, "/api/register")
    api.add_resource(Dashboard, "/api/dashboard")
    api.add_resource(DocumentResource, "/api/documents", "/api/documents/<int:id>")
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
    api.add_resource(CheckUserRole, "/api/check-user-role/<int:user_id>")

    @app.route("/")
    def index():
        return jsonify({
            "message": "VendorSync API is running!",
            "version": "1.0.0",
            "endpoints": {
                "health": "/api/health",
                "login": "/api/login",
                "register": "/api/register",
                "dashboard": "/api/dashboard",
                "seed": "/api/seed-db"
            }
        }), 200

    @app.route("/api/health")
    def health_check():
        return jsonify({
            "status": "ok",
            "message": "Backend running successfully",
            "database": "connected"
        }), 200

    # ✅ Get vendor verification status
    @app.route('/api/vendor/status', methods=['GET'])
    @jwt_required()
    def get_vendor_status():
        vendor = Vendor.query.filter_by(user_id=get_jwt_identity()).first()
        return {'is_approved': vendor.is_approved if vendor else False}

    # ✅ Create assignment
    @app.route('/api/assignments', methods=['POST'])
    @jwt_required()
    def create_assignment():
        data = request.get_json()
        order_id = data.get('order_id')
        vendor_id = data.get('vendor_id')

        if not order_id or not vendor_id:
            return jsonify({"message": "Missing order_id or vendor_id"}), 400

        existing_assignment = OrderAssignment.query.filter_by(order_id=order_id, vendor_id=vendor_id).first()
        if existing_assignment:
            return jsonify({"message": "Assignment already exists"}), 400

        assignment = OrderAssignment(order_id=order_id, vendor_id=vendor_id)
        db.session.add(assignment)
        db.session.commit()

        return jsonify({"message": "Assignment created successfully", "assignment_id": assignment.id}), 201

    class SeedDB(Resource):
        def get(self):
            try:
                from backend.db_seed import seed_all
                
                print("Starting database seeding...")
                seed_all()
                
                return {
                    "message": "Database seeded successfully",
                    "credentials": {
                        "manager": "manager@example.com / password123",
                        "staff": "staff@example.com / password123",
                        "vendor": "vendor@example.com / password123"
                    }
                }, 200
            except Exception as e:
                db.session.rollback()
                print(f"Error during seeding: {str(e)}")
                return {
                    "message": f"Error during seeding: {str(e)}"
                }, 500

    api.add_resource(SeedDB, "/api/seed-db")

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'message': 'Token has expired',
            'error': 'token_expired'
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'message': 'Invalid token',
            'error': 'invalid_token'
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'message': 'Authorization token is missing',
            'error': 'authorization_required'
        }), 401

    return app
