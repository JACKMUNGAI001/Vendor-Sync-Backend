from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from resources.auth import Login
from resources.user import UserResource
from resources.dashboard import Dashboard
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
api = Api(app)
jwt = JWTManager(app)

api.add_resource(Login, '/login')
api.add_resource(UserResource, '/users')
api.add_resource(Dashboard, '/dashboard')

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)