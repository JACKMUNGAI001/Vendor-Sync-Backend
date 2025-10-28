from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from resources.auth import Login
from resources.user import UserResource
from resources.dashboard import Dashboard
from resources.order import OrderResource, OrderVendorResource, OrderAssignmentResource
from resources.quote import QuoteResource
from resources.document import DocumentResource
from resources.search import SearchResource
from resources.upload import UploadResource
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
jwt = JWTManager(app)

api.add_resource(Login, '/login')
api.add_resource(UserResource, '/users')
api.add_resource(Dashboard, '/dashboard')
api.add_resource(OrderResource, '/orders', '/orders/<int:id>')
api.add_resource(OrderVendorResource, '/orders/vendor')
api.add_resource(OrderAssignmentResource, '/order-assignments')
api.add_resource(QuoteResource, '/quotes', '/quotes/<int:id>')
api.add_resource(DocumentResource, '/documents')
api.add_resource(SearchResource, '/search')
api.add_resource(UploadResource, '/upload')

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)