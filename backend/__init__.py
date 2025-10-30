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

    CORS(app, resources={r"/api/*": {"origins": "https://wondrous-twilight-609097.netlify.app"}})

    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    from backend.resources.auth import Login, Register

    api = Api(app)

    api.add_resource(Login, "/api/login")
    api.add_resource(Register, "/api/register")

    @app.route("/")
    def index():
        return "Vendor Sync Backend is running!"

    @app.route("/api/health")
    def health_check():
        return jsonify({"status": "ok", "message": "Backend running successfully"}), 200

    return app
