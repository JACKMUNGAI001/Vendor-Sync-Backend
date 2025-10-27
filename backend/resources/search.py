from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from algoliasearch.search_client import SearchClient
from config import Config

class SearchResource(Resource):
    @jwt_required()
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('query', required=True)
        args = parser.parse_args()

        client = SearchClient.create(Config.ALGOLIA_APP_ID, Config.ALGOLIA_API_KEY)
        index = client.init_index('vendorsync')
        results = index.search(args['query'])
        return results['hits'], 200