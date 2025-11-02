from flask_restful import Resource

class SearchResource(Resource):
    def get(self):
        return {'message': 'Search endpoint'}, 200