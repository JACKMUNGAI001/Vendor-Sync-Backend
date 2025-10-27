from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User

class Dashboard(Resource):
    @jwt_required()
    def get(self):
        user = User.query.get(get_jwt_identity())
        data = []
        return data, 200