from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.quote import Quote
from backend.models.user import User
from backend.models.purchase_order import PurchaseOrder
from backend.models.vendor import Vendor
from backend import db
# from backend.services.email_service import email_service # Temporarily commented out

class QuoteResource(Resource):
    @jwt_required()
    def post(self):
        user = User.query.get(get_jwt_identity())
        if not user or user.role.name != 'vendor':
            return {'message': 'Only vendors can submit quotes'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('order_id', type=int, required=True, help='Order ID is required')
        parser.add_argument('price', type=float, required=True, help='Price is required')
        parser.add_argument('notes', type=str)
        args = parser.parse_args()

        order = PurchaseOrder.query.get(args['order_id'])
        if not order:
            return {'message': 'Order not found'}, 404

        if order.vendor_id != user.id:
            return {'message': 'You can only submit quotes for your own orders'}, 403

        existing_quote = Quote.query.filter_by(order_id=args['order_id'], vendor_id=user.id).first()
        if existing_quote:
            return {'message': 'You have already submitted a quote for this order'}, 400

        quote = Quote(
            vendor_id=user.id,
            order_id=args['order_id'],
            price=args['price'],
            notes=args.get('notes'),
            status='pending'
        )

        try:
            db.session.add(quote)
            db.session.commit()

            # Send email to manager # Temporarily commented out
            # manager = User.query.get(order.manager_id)
            # if manager:
            #     subject = f"New Quote Submitted for Order #{order.id}"
            #     html_content = f"<p>Dear {manager.first_name},</p>\n<p>A new quote has been submitted by {user.first_name} {user.last_name} for Order #{order.id}.</p>\n<p>Quote Price: ${quote.price}</p>\n<p>Notes: {quote.notes}</p>\n<p>Please review the quote in VendorSync.</p>"
            #     email_service.send_email(manager.email, subject, html_content)

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
            
            if user.role.name == 'vendor' and quote.vendor.id != user.id:
                return {'message': 'Access denied'}, 403
            if user.role.name == 'manager' and quote.order.manager_id != user.id:
                return {'message': 'Access denied'}, 403
            
            return quote.to_dict(), 200

        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default=1)
        parser.add_argument('per_page', type=int, default=10)
        parser.add_argument('status', type=str)
        args = parser.parse_args()

        if user.role.name == 'manager':
            query = Quote.query.join(PurchaseOrder).filter(PurchaseOrder.manager_id == user.id)
        elif user.role.name == 'vendor':
            query = Quote.query.filter_by(vendor_id=user.id)
        else:
            return {'message': 'Access denied'}, 403

        if args['status']:
            query = query.filter_by(status=args['status'])

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
        if not user or user.role.name != 'manager':
            return {'message': 'Only managers can update quote status'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('status', required=True, help='Status is required')
        args = parser.parse_args()

        quote = Quote.query.get(id)
        if not quote:
            return {'message': 'Quote not found'}, 404

        if quote.order.manager_id != user.id:
            return {'message': 'You can only update quotes for your own orders'}, 403

        valid_statuses = ['pending', 'accepted', 'rejected']
        if args['status'] not in valid_statuses:
            return {'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}, 400

        old_status = quote.status
        quote.status = args['status']

        try:
            db.session.commit()

            # Send email to vendor if status changed # Temporarily commented out
            # if old_status != quote.status:
            #     vendor = Vendor.query.get(quote.vendor_id)
            #     if vendor:
            #         subject = f"Your Quote for Order #{quote.order.id} has been {quote.status.capitalize()}"
            #         html_content = f"<p>Dear {vendor.name},</p>\n<p>Your quote for Order #{quote.order.id} has been <b>{quote.status}</b> by the manager.</p>\n<p>Please log in to VendorSync for more details.</p>"
            #         email_service.send_email(vendor.email, subject, html_content)

            return {
                'message': 'Quote updated successfully',
                'quote': quote.to_dict()
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Failed to update quote: {str(e)}'}, 500