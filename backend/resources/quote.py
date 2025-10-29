from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.quote import Quote
from backend.models.purchase_order import PurchaseOrder
from backend.models.user import User
from backend.models.vendor import Vendor
from backend import db

class QuoteResource(Resource):
    @jwt_required()
    def get(self, id=None):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if id:
            quote = Quote.query.get(id)
            if not quote:
                return {'message': 'Quote not found'}, 404
            return quote.to_dict(), 200
        
        if user.role.name == 'vendor':
            vendor = Vendor.query.filter_by(contact_email=user.email).first()
            quotes = Quote.query.filter_by(vendor_id=vendor.id).all() if vendor else []
        elif user.role.name == 'manager':
            quotes = Quote.query.all()
        else:
            return {'message': 'Access denied'}, 403
            
        return {'quotes': [quote.to_dict() for quote in quotes]}, 200

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role.name != 'vendor':
            return {'message': 'Only vendors can submit quotes'}, 403
            
        vendor = Vendor.query.filter_by(contact_email=user.email).first()
        if not vendor:
            return {'message': 'Vendor profile not found'}, 404

        parser = reqparse.RequestParser()
        parser.add_argument('order_id', type=int, required=True)
        parser.add_argument('price', type=float, required=True)
        parser.add_argument('notes', type=str)
        args = parser.parse_args()

        order = PurchaseOrder.query.get(args['order_id'])
        if not order:
            return {'message': 'Order not found'}, 404

        quote = Quote(
            vendor_id=vendor.id,
            order_id=args['order_id'],
            price=args['price'],
            notes=args.get('notes'),
            status='pending'
        )

        db.session.add(quote)
        db.session.commit()

        return {
            'message': 'Quote submitted successfully',
            'quote': quote.to_dict()
        }, 201

    @jwt_required()
    def patch(self, id):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role.name != 'manager':
            return {'message': 'Only managers can update quotes'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('status', required=True, choices=('accepted', 'rejected'))
        args = parser.parse_args()

        quote = Quote.query.get(id)
        if not quote:
            return {'message': 'Quote not found'}, 404

        quote.status = args['status']
        db.session.commit()

        return {
            'message': f'Quote {args["status"]} successfully',
            'quote': quote.to_dict()
        }, 200