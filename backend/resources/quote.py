from flask_restful import Resource

class QuoteResource(Resource):
    def get(self):
        return {'message': 'Quote endpoint'}, 200