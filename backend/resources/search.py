from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from flask import current_app
# from backend.services.algolia_service import AlgoliaService # Temporarily commented out

# algolia_service = AlgoliaService() # Temporarily commented out

class SearchResource(Resource):
    @jwt_required()
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('query', required=True, help='Search query is required')
        args = parser.parse_args()

        search_query = args['query']
        results = []

        try:
            # if current_app.config.get('ALGOLIA_ENABLED', False):
            #     algolia_results = algolia_service.index.search(search_query)
            #     hits = algolia_results['hits']

            #     for hit in hits:
            #         # Algolia results will already contain the objectID and type if indexed correctly
            #         results.append(hit)
            # else:
                # Fallback to current database search if Algolia is not enabled
            from backend.models.vendor import Vendor
            from backend.models.purchase_order import PurchaseOrder
            from backend.models.quote import Quote
            from backend.models.requirement import Requirement
            
            # Search vendors
            vendors = Vendor.query.filter(
                (Vendor.name.ilike(f'%{search_query}%')) |
                (Vendor.email.ilike(f'%{search_query}%'))
            ).filter_by(is_verified=True).all()

            for vendor in vendors:
                results.append({
                    'id': vendor.id,
                    'type': 'vendor',
                    'name': vendor.name,
                    'email': vendor.email,
                    'description': f'Vendor • {vendor.email}'
                })

            # Search orders
            orders = PurchaseOrder.query.filter(
                (PurchaseOrder.order_number.ilike(f'%{search_query}%'))
            ).all()

            for order in orders:
                results.append({
                    'id': order.id,
                    'type': 'order',
                    'name': f'Order #{order.id}',
                    'status': order.status,
                    'description': f'Order • {order.status}'
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
            
            # Search requirements
            requirements = Requirement.query.filter(
                (Requirement.item_name.ilike(f'%{search_query}%')) |
                (Requirement.specifications.ilike(f'%{search_query}%'))
            ).all()

            for requirement in requirements:
                results.append({
                    'id': requirement.id,
                    'type': 'requirement',
                    'name': requirement.item_name,
                    'quantity': requirement.quantity,
                    'description': f'Requirement • {requirement.item_name}'
                })

            return results, 200

        except Exception as e:
            return {'message': f'Search error: {str(e)}'}, 500