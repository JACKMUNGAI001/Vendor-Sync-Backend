from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.user import User

class Dashboard(Resource):
    @jwt_required()
    def get(self):
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return {'message': 'User not found'}, 404

            data = []

            if user.role.name == 'manager':
                data = [
                    {'id': 1, 'description': 'Sample Manager Order 1 - pending'},
                    {'id': 2, 'description': 'Sample Manager Order 2 - completed'}
                ]

            elif user.role.name == 'staff':
                data = [
                    {'id': 1, 'description': 'Assigned Order 1 - in progress'},
                    {'id': 2, 'description': 'Assigned Order 2 - pending'}
                ]

            elif user.role.name == 'vendor':
                data = [
                    {'id': 1, 'description': 'Vendor Order 1 - quoted'},
                    {'id': 2, 'description': 'Vendor Order 2 - delivered'}
                ]

            else:
                return {'message': 'Invalid role'}, 400

            return data, 200

        except Exception as e:
            return {'message': f'Dashboard error: {str(e)}'}, 500