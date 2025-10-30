from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.vendor_category import VendorCategory
from backend.models.user import User
from backend import db

class VendorCategoryResource(Resource):
    @jwt_required()
    def get(self, id=None):
        if id:
            category = VendorCategory.query.get(id)
            if not category:
                return {'message': 'Category not found'}, 404
            return category.to_dict(), 200

        categories = VendorCategory.query.all()
        return {'categories': [cat.to_dict() for cat in categories]}, 200

    @jwt_required()
    def post(self):
        user = User.query.get(get_jwt_identity())
        if not user or user.role.name != 'manager':
            return {'message': 'Only procurement managers can create categories'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True, help='Category name is required')
        args = parser.parse_args()

        if VendorCategory.query.filter_by(name=args['name']).first():
            return {'message': 'Category already exists'}, 400

        category = VendorCategory(name=args['name'])

        try:
            db.session.add(category)
            db.session.commit()
            return {'message': 'Category created successfully', 'category': category.to_dict()}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Failed to create category: {str(e)}'}, 500

    @jwt_required()
    def patch(self, id):
        user = User.query.get(get_jwt_identity())
        if not user or user.role.name != 'manager':
            return {'message': 'Only procurement managers can update categories'}, 403

        category = VendorCategory.query.get(id)
        if not category:
            return {'message': 'Category not found'}, 404

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str)
        args = parser.parse_args()

        if args['name']:
            if VendorCategory.query.filter_by(name=args['name']).first():
                return {'message': 'Category name already exists'}, 400
            category.name = args['name']

        try:
            db.session.commit()
            return {'message': 'Category updated successfully', 'category': category.to_dict()}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Failed to update category: {str(e)}'}, 500

    @jwt_required()
    def delete(self, id):
        user = User.query.get(get_jwt_identity())
        if not user or user.role.name != 'manager':
            return {'message': 'Only procurement managers can delete categories'}, 403

        category = VendorCategory.query.get(id)
        if not category:
            return {'message': 'Category not found'}, 404

        try:
            db.session.delete(category)
            db.session.commit()
            return {'message': 'Category deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Failed to delete category: {str(e)}'}, 500
