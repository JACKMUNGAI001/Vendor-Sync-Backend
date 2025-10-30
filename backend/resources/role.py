from flask_restful import Resource
from backend.models.role import Role

class RoleResource(Resource):
    def get(self):
        try:
            roles = Role.query.all()
            return {
                'roles': [
                    {'id': role.id, 'name': role.name} for role in roles
                ]
            }, 200
        except Exception as e:
            return {'message': f'Error fetching roles: {str(e)}'}, 500
