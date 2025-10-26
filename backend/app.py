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