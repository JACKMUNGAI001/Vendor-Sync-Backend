from flask_restful import Resource
from backend.models.purchase_order import PurchaseOrder
from backend.models.order_assignment import OrderAssignment

class OrderResource(Resource):
    def get(self, id=None):
        if id:
            return {'message': f'Order {id}'}, 200
        return {'message': 'Orders list'}, 200
    
    def post(self):
        return {'message': 'Order created'}, 201

class OrderVendorResource(Resource):
    def get(self):
        return {'message': 'Vendor orders'}, 200

class OrderAssignmentResource(Resource):
    def get(self, assignment_id=None):
        return {'message': 'Order assignments'}, 200
    
    def post(self):
        return {'message': 'Assignment created'}, 201