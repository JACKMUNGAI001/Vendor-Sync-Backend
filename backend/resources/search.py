from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from backend.models.vendor import Vendor
from backend.models.purchase_order import PurchaseOrder
from backend.models.quote import Quote
from backend.models.user import User

class SearchResource(Resource):
    @jwt_required()
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('query', required=True, help='Search query is required')
        args = parser.parse_args()

        search_query = args['query'].lower()
        results = []

        try:
            # Search vendors
            vendors = Vendor.query.filter(
                (Vendor.name.ilike(f'%{search_query}%')) |
                (Vendor.contact_email.ilike(f'%{search_query}%')) |
                (Vendor.business_type.ilike(f'%{search_query}%'))
            ).filter_by(is_approved=True).all()

            for vendor in vendors:
                results.append({
                    'id': vendor.id,
                    'type': 'vendor',
                    'name': vendor.name,
                    'contact_email': vendor.contact_email,
                    'business_type': vendor.business_type,
                    'description': f'Vendor • {vendor.contact_email}'
                })

            # Search orders
            orders = PurchaseOrder.query.filter(
                (PurchaseOrder.material_list.ilike(f'%{search_query}%')) |
                (PurchaseOrder.special_instructions.ilike(f'%{search_query}%'))
            ).all()

            for order in orders:
                material_count = len(order.material_list) if order.material_list else 0
                results.append({
                    'id': order.id,
                    'type': 'order',
                    'name': f'Order #{order.id}',
                    'material_list': str(order.material_list),
                    'status': order.status,
                    'description': f'Order • {material_count} materials • {order.status}'
                })

            # Search quotes
            quotes = Quote.query.filter(
                (Quote.notes.ilike(f'%{search_query}%'))
            ).all()

            for quote in quotes:
                results.append({
                    'id': quote.id,
                    'type': 'quote',
                    'name': f'Quote #{quote.id}',
                    'price': float(quote.price) if quote.price else 0,
                    'status': quote.status,
                    'description': f'Quote • ${float(quote.price) if quote.price else 0} • {quote.status}'
                })

            return results, 200

        except Exception as e:
            return {'message': f'Search error: {str(e)}'}, 500