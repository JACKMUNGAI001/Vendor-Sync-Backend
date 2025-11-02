from flask_restful import Resource

class Dashboard(Resource):
    def get(self):
        return {'message': 'Dashboard endpoint'}, 200