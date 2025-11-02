from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.vendor import Vendor
from backend.models.user import User
from backend import db

class VendorResource(Resource):
    @jwt_required()
    def get(self, id=None):
        user = User.query.get(get_jwt_identity())
        if not user:
            return {'message': 'User not found'}, 404

        if id:
            vendor = Vendor.query.get(id)
            if not vendor:
                return {'message': 'Vendor not found'}, 404
            
            if user.role.name == 'vendor':
                vendor_user = Vendor.query.filter_by(email=user.email).first()
                if not vendor_user or vendor_user.id != id:
                    return {'message': 'Access denied'}, 403
            
            return vendor.to_dict(), 200

        parser = reqparse.RequestParser()
        parser.add_argument('verified', type=lambda x: x.lower() == 'true', location='args')
        parser.add_argument('category_id', type=int, location='args')
        args = parser.parse_args()

        if user.role.name != 'manager':
            if user.role.name == 'vendor':
                vendor = Vendor.query.filter_by(email=user.email).first()
                if vendor:
                    return {'vendors': [vendor.to_dict()]}, 200
                return {'vendors': []}, 200
            return {'message': 'Access denied'}, 403

        query = Vendor.query
        
        if args['verified'] is not None:
            query = query.filter_by(is_verified=args['verified'])
        
        if args['category_id']:
            query = query.filter_by(category_id=args['category_id'])
        
        vendors = query.order_by(Vendor.created_at.desc()).all()
        return {'vendors': [vendor.to_dict() for vendor in vendors]}, 200

    @jwt_required()
    def post(self):
        user = User.query.get(get_jwt_identity())
        if not user or user.role.name != 'manager':
            return {'message': 'Only procurement managers can create vendors'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True, help='Vendor name is required')
        parser.add_argument('email', required=True, help='Vendor email is required')
        parser.add_argument('phone', type=str)
        parser.add_argument('address', type=str)
        parser.add_argument('company_name', type=str)
        parser.add_argument('contact_person', type=str)
        parser.add_argument('category_id', type=int)
        parser.add_argument('is_verified', type=bool, default=False)
        args = parser.parse_args()

        if Vendor.query.filter_by(email=args['email']).first():
            return {'message': 'Vendor with this email already exists'}, 400

        vendor = Vendor(
            name=args['name'],
            email=args['email'],
            phone=args['phone'],
            address=args['address'],
            company_name=args['company_name'],
            contact_person=args['contact_person'],
            category_id=args['category_id'],
            is_verified=args.get('is_verified', False)
        )

        try:
            db.session.add(vendor)
            db.session.commit()

            return {'message': 'Vendor created successfully', 'vendor': vendor.to_dict()}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Failed to create vendor: {str(e)}'}, 500

    @jwt_required()
    def patch(self, id):
        user = User.query.get(get_jwt_identity())
        if not user:
            return {'message': 'User not found'}, 404

        vendor = Vendor.query.get(id)
        if not vendor:
            return {'message': 'Vendor not found'}, 404

        if user.role.name == 'vendor':
            vendor_user = Vendor.query.filter_by(email=user.email).first()
            if not vendor_user or vendor_user.id != id:
                return {'message': 'Access denied'}, 403
        elif user.role.name != 'manager':
            return {'message': 'Only managers and vendors can update vendor profiles'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str)
        parser.add_argument('email', type=str)
        parser.add_argument('phone', type=str)
        parser.add_argument('address', type=str)
        parser.add_argument('company_name', type=str)
        parser.add_argument('contact_person', type=str)
        parser.add_argument('category_id', type=int)
        parser.add_argument('is_verified', type=bool)
        args = parser.parse_args()

        if args.get('is_verified') is not None and user.role.name != 'manager':
            return {'message': 'Only managers can verify vendors'}, 403

        if args['name']:
            vendor.name = args['name']
        if args['email']:
            if Vendor.query.filter_by(email=args['email']).first() and args['email'] != vendor.email:
                return {'message': 'Vendor with this email already exists'}, 400
            vendor.email = args['email']
        if args['phone']:
            vendor.phone = args['phone']
        if args['address']:
            vendor.address = args['address']
        if args['company_name']:
            vendor.company_name = args['company_name']
        if args['contact_person']:
            vendor.contact_person = args['contact_person']
        if args['category_id']:
            vendor.category_id = args['category_id']
        if args.get('is_verified') is not None and user.role.name == 'manager':
            vendor.is_verified = args['is_verified']

        try:
            db.session.commit()
            return {'message': 'Vendor updated successfully', 'vendor': vendor.to_dict()}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Failed to update vendor: {str(e)}'}, 500

    @jwt_required()
    def delete(self, id):
        user = User.query.get(get_jwt_identity())
        if not user or user.role.name != 'manager':
            return {'message': 'Only procurement managers can delete vendors'}, 403

        vendor = Vendor.query.get(id)
        if not vendor:
            return {'message': 'Vendor not found'}, 404

        try:
            db.session.delete(vendor)
            db.session.commit()
            return {'message': 'Vendor deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Failed to delete vendor: {str(e)}'}, 500