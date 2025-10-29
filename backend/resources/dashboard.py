from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.user import User

class Dashboard(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return {'message': 'User not found'}, 404

        # Return sample data based on user role
        sample_data = [
            {'id': 1, 'description': f'Sample {user.role.name} task 1 - pending'},
            {'id': 2, 'description': f'Sample {user.role.name} task 2 - in progress'},
            {'id': 3, 'description': f'Sample {user.role.name} task 3 - completed'}
        ]

        return sample_data, 200