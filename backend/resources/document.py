from flask_restful import Resource

class DocumentResource(Resource):
    def get(self):
        return {'message': 'Document endpoint'}, 200