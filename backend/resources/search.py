from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from algoliasearch.search_client import SearchClient
from backend.config import Config

class SearchResource(Resource):
    @jwt_required()
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('query', required=True)
        args = parser.parse_args()

        sample_results = [
            {
                'objectID': '1',
                'name': 'ABC Construction Supplies',
                'type': 'vendor',
                'status': 'approved'
            },
            {
                'objectID': '2', 
                'name': 'Order #123 - Cement Delivery',
                'type': 'order',
                'status': 'pending'
            },
            {
                'objectID': '3',
                'name': 'Quote #456 - $1500.00',
                'type': 'quote', 
                'status': 'pending',
                'price': 1500.00
            }
        ]

        # Filter results based on query
        query = args['query'].lower()
        filtered_results = [
            result for result in sample_results 
            if query in result['name'].lower() or query in result['type']
        ]

        return {'hits': filtered_results}, 200