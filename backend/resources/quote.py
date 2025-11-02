from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.quote import Quote
from backend.models.user import User
from backend.models.purchase_order import PurchaseOrder
from backend.models.vendor import Vendor
from backend.models.order_assignment import OrderAssignment
from backend import db

class QuoteResource(Resource):
    @jwt_required()
    def post(self):
        user = User.query.get(get_jwt_identity())
        if not user or user.role.name != 'vendor':
            return {'message': 'Only vendors can submit quotes'}, 403

        vendor = Vendor.query.filter_by(email=user.email).first()
        if not vendor:
            return {'message': 'Vendor profile not found'}, 404
        
        if not vendor.is_verified:
            return {'message': 'Only verified vendors can submit quotes'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('order_id', type=int, required=True, help='Order ID is required')
        parser.add_argument('price', type=float, required=True, help='Price is required')
        parser.add_argument('notes', type=str)
        parser.add_argument('delivery_days', type=int, default=7)
        args = parser.parse_args()

        if args['price'] <= 0:
            return {'message': 'Price must be greater than 0'}, 400

        order = PurchaseOrder.query.get(args['order_id'])
        if not order:
            return {'message': 'Order not found'}, 404

        if order.vendor_id != vendor.id:
            return {'message': 'You can only submit quotes for orders assigned to you'}, 403

        existing_quote = Quote.query.filter_by(order_id=args['order_id'], vendor_id=vendor.id).first()
        if existing_quote:
            return {'message': 'You have already submitted a quote for this order. Use PATCH to update it.'}, 400

        quote = Quote(
            vendor_id=vendor.id,
            order_id=args['order_id'],
            price=args['price'],
            notes=args.get('notes'),
            status='pending'
        )

        try:
            db.session.add(quote)
            db.session.commit()

            return {
                'message': 'Quote submitted successfully',
                'quote': quote.to_dict()
            }, 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Failed to submit quote: {str(e)}'}, 500

    @jwt_required()
    def get(self, id=None):
        user = User.query.get(get_jwt_identity())
        if not user:
            return {'message': 'User not found'}, 404

        if id:
            quote = Quote.query.get(id)
            if not quote:
                return {'message': 'Quote not found'}, 404
            
            if user.role.name == 'vendor':
                vendor = Vendor.query.filter_by(email=user.email).first()
                if not vendor or quote.vendor_id != vendor.id:
                    return {'message': 'Access denied'}, 403
            elif user.role.name == 'manager':
                if quote.order.manager_id != user.id:
                    return {'message': 'Access denied'}, 403
            elif user.role.name == 'staff':
                assigned = any(a.staff_id == user.id for a in quote.order.assignments)
                if not assigned:
                    return {'message': 'Access denied'}, 403
            
            return quote.to_dict(), 200

        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default=1, location='args')
        parser.add_argument('per_page', type=int, default=10, location='args')
        parser.add_argument('status', type=str, location='args')
        parser.add_argument('order_id', type=int, location='args')
        args = parser.parse_args()

        if user.role.name == 'manager':
            query = Quote.query.join(PurchaseOrder).filter(PurchaseOrder.manager_id == user.id)
        elif user.role.name == 'vendor':
            vendor = Vendor.query.filter_by(email=user.email).first()
            if not vendor:
                return {'quotes': [], 'total_pages': 0, 'current_page': 1, 'total_quotes': 0}, 200
            query = Quote.query.filter_by(vendor_id=vendor.id)
        elif user.role.name == 'staff':
            query = Quote.query.join(PurchaseOrder).join(OrderAssignment).filter(
                OrderAssignment.staff_id == user.id
            )
        else:
            return {'message': 'Access denied'}, 403

        if args['status']:
            query = query.filter(Quote.status == args['status'])
        
        if args['order_id']:
            query = query.filter(Quote.order_id == args['order_id'])

        pagination = query.order_by(Quote.created_at.desc()).paginate(
            page=args['page'], 
            per_page=args['per_page'],
            error_out=False
        )

        return {
            'quotes': [quote.to_dict() for quote in pagination.items],
            'total_pages': pagination.pages,
            'current_page': pagination.page,
            'total_quotes': pagination.total,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }, 200

    @jwt_required()
    def patch(self, id):
        user = User.query.get(get_jwt_identity())
        if not user:
            return {'message': 'User not found'}, 404

        quote = Quote.query.get(id)
        if not quote:
            return {'message': 'Quote not found'}, 404

        parser = reqparse.RequestParser()
        parser.add_argument('status', type=str)
        parser.add_argument('price', type=float)
        parser.add_argument('notes', type=str)
        args = parser.parse_args()

        if user.role.name == 'manager':
            if quote.order.manager_id != user.id:
                return {'message': 'You can only update quotes for your own orders'}, 403
            
            if args.get('status'):
                valid_statuses = ['pending', 'accepted', 'rejected']
                if args['status'] not in valid_statuses:
                    return {'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}, 400

                old_status = quote.status
                quote.status = args['status']

                if args['status'] == 'accepted' and old_status != 'accepted':
                    quote.order.status = 'ordered'

        elif user.role.name == 'vendor':
            vendor = Vendor.query.filter_by(email=user.email).first()
            if not vendor or quote.vendor_id != vendor.id:
                return {'message': 'You can only update your own quotes'}, 403
            
            if quote.status != 'pending':
                return {'message': 'Cannot update quote after it has been reviewed'}, 400
            
            if args.get('price'):
                if args['price'] <= 0:
                    return {'message': 'Price must be greater than 0'}, 400
                quote.price = args['price']
            
            if args.get('notes') is not None:
                quote.notes = args['notes']
        else:
            return {'message': 'Access denied'}, 403

        try:
            db.session.commit()
            return {
                'message': 'Quote updated successfully',
                'quote': quote.to_dict()
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Failed to update quote: {str(e)}'}, 500

    @jwt_required()
    def delete(self, id):
        user = User.query.get(get_jwt_identity())
        if not user:
            return {'message': 'User not found'}, 404

        quote = Quote.query.get(id)
        if not quote:
            return {'message': 'Quote not found'}, 404

        if user.role.name == 'vendor':
            vendor = Vendor.query.filter_by(email=user.email).first()
            if not vendor or quote.vendor_id != vendor.id:
                return {'message': 'You can only delete your own quotes'}, 403
            
            if quote.status != 'pending':
                return {'message': 'Cannot delete quote after it has been reviewed'}, 400
        elif user.role.name == 'manager':
            if quote.order.manager_id != user.id:
                return {'message': 'Access denied'}, 403
        else:
            return {'message': 'Access denied'}, 403

        try:
            db.session.delete(quote)
            db.session.commit()
            return {'message': 'Quote deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Failed to delete quote: {str(e)}'}, 500