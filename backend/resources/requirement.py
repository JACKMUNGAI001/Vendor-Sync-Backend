from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.requirement import Requirement
from backend.models.user import User
from backend import db

class RequirementResource(Resource):
    @jwt_required()
    def get(self, id=None):
        user = User.query.get(get_jwt_identity())
        if not user or user.role.name != 'manager':
            return {'message': 'Only procurement managers can view requirements'}, 403

        if id:
            requirement = Requirement.query.get(id)
            if not requirement or requirement.manager_id != user.id:
                return {'message': 'Requirement not found or access denied'}, 404
            return requirement.to_dict(), 200

        requirements = Requirement.query.filter_by(manager_id=user.id).all()
        return {'requirements': [req.to_dict() for req in requirements]}, 200

    @jwt_required()
    def post(self):
        user = User.query.get(get_jwt_identity())
        if not user or user.role.name != 'manager':
            return {'message': 'Only procurement managers can create requirements'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('item_name', required=True, help='Item name is required')
        parser.add_argument('quantity', type=int, required=True, help='Quantity is required')
        parser.add_argument('specifications', type=str)
        args = parser.parse_args()

        requirement = Requirement(
            item_name=args['item_name'],
            quantity=args['quantity'],
            specifications=args['specifications'],
            manager_id=user.id
        )

        try:
            db.session.add(requirement)
            db.session.commit()
            return {'message': 'Requirement created successfully', 'requirement': requirement.to_dict()}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Failed to create requirement: {str(e)}'}, 500

    @jwt_required()
    def patch(self, id):
        user = User.query.get(get_jwt_identity())
        if not user or user.role.name != 'manager':
            return {'message': 'Only procurement managers can update requirements'}, 403

        requirement = Requirement.query.get(id)
        if not requirement or requirement.manager_id != user.id:
            return {'message': 'Requirement not found or access denied'}, 404

        parser = reqparse.RequestParser()
        parser.add_argument('item_name', type=str)
        parser.add_argument('quantity', type=int)
        parser.add_argument('specifications', type=str)
        args = parser.parse_args()

        if args['item_name']:
            requirement.item_name = args['item_name']
        if args['quantity']:
            requirement.quantity = args['quantity']
        if args['specifications']:
            requirement.specifications = args['specifications']

        try:
            db.session.commit()
            return {'message': 'Requirement updated successfully', 'requirement': requirement.to_dict()}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Failed to update requirement: {str(e)}'}, 500

    @jwt_required()
    def delete(self, id):
        user = User.query.get(get_jwt_identity())
        if not user or user.role.name != 'manager':
            return {'message': 'Only procurement managers can delete requirements'}, 403

        requirement = Requirement.query.get(id)
        if not requirement or requirement.manager_id != user.id:
            return {'message': 'Requirement not found or access denied'}, 404

        try:
            db.session.delete(requirement)
            db.session.commit()
            return {'message': 'Requirement deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Failed to delete requirement: {str(e)}'}, 500
