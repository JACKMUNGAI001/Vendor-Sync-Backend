from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.vendor import Vendor
from backend.models.user import User
from backend import db
# from backend.services.email_service import email_service # Temporarily commented out

class VendorResource(Resource):
    @jwt_required()
    def get(self, id=None):
        if id:
            vendor = Vendor.query.get(id)
            if not vendor:
                return {'message': 'Vendor not found'}, 404
            return vendor.to_dict(), 200

        parser = reqparse.RequestParser()
        parser.add_argument('verified', type=bool)
        args = parser.parse_args()

        query = Vendor.query
        if args['verified'] is not None:
            query = query.filter_by(is_verified=args['verified'])
        
        vendors = query.all()
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
            category_id=args['category_id']
        )

        try:
            db.session.add(vendor)
            db.session.commit()

            # Send welcome email to new vendor # Temporarily commented out
            # subject = "Welcome to VendorSync!"
            # html_content = f"<p>Dear {vendor.contact_person or vendor.name},</p>\n<p>Your vendor account for {vendor.company_name or 'VendorSync'} has been created.</p>\n<p>You can now log in to VendorSync using your email ({vendor.email}) and a temporary password (if provided, otherwise you can set one up).</p>\n<p>We look forward to working with you!</p>"
            # email_service.send_email(vendor.email, subject, html_content)

            return {'message': 'Vendor created successfully', 'vendor': vendor.to_dict()}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Failed to create vendor: {str(e)}'}, 500

    @jwt_required()
    def patch(self, id):
        user = User.query.get(get_jwt_identity())
        if not user or user.role.name != 'manager':
            return {'message': 'Only procurement managers can update vendors'}, 403

        vendor = Vendor.query.get(id)
        if not vendor:
            return {'message': 'Vendor not found'}, 404

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
        if args['is_verified'] is not None:
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