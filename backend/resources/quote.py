from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.quote import Quote
from models.user import User
from models.purchase_order import PurchaseOrder
from app import db
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config import Config

class QuoteResource(Resource):
    @jwt_required()
    def post(self):
        user = User.query.get(get_jwt_identity())
        if user.role.name != 'vendor':
            return {'message': 'Unauthorized'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('order_id', type=int, required=True)
        parser.add_argument('price', type=float, required=True)
        args = parser.parse_args()

        order = PurchaseOrder.query.get(args['order_id'])
        if not order:
            return {'message': 'Order not found'}, 404

        quote = Quote(
            vendor_id=user.id,
            order_id=args['order_id'],
            price=args['price'],
            status='pending'
        )
        db.session.add(quote)
        db.session.commit()

        message = Mail(
            from_email='no-reply@vendorsync.com',
            to_emails=order.manager.email,
            subject='New Quote Submitted',
            plain_text_content=f'Quote #{quote.id} for Order #{order.id} submitted.'
        )
        sg = SendGridAPIClient(Config.SENDGRID_API_KEY)
        sg.send(message)

        return {'message': 'Quote submitted'}, 201

    @jwt_required()
    def patch(self, id):
        if User.query.get(get_jwt_identity()).role.name != 'manager':
            return {'message': 'Unauthorized'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('status', required=True)
        args = parser.parse_args()

        quote = Quote.query.get(id)
        if not quote:
            return {'message': 'Quote not found'}, 404

        quote.status = args['status']
        db.session.commit()

        message = Mail(
            from_email='no-reply@vendorsync.com',
            to_emails=quote.vendor.contact_email,
            subject='Quote Status Updated',
            plain_text_content=f'Your Quote #{quote.id} is now {quote.status}.'
        )
        sg = SendGridAPIClient(Config.SENDGRID_API_KEY)
        sg.send(message)

        return {'message': 'Quote updated'}, 200