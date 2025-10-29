from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.purchase_order import PurchaseOrder
from backend.models.vendor import Vendor
from backend import db

class OrderResource(Resource):
    @jwt_required()
    def get(self, id=None):
        if id:
            order = PurchaseOrder.query.get(id)
            if not order:
                return {'message': 'Order not found'}, 404
            return order.to_dict(), 200
        
        # Return all orders
        orders = PurchaseOrder.query.all()
        return {'orders': [order.to_dict() for order in orders]}, 200

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        
        parser = reqparse.RequestParser()
        parser.add_argument('vendor_id', type=int, required=True)
        parser.add_argument('material_name', required=True)
        parser.add_argument('quantity', type=int, required=True)
        parser.add_argument('unit', required=True)
        args = parser.parse_args()

        vendor = Vendor.query.get(args['vendor_id'])
        if not vendor:
            return {'message': 'Vendor not found'}, 404

        material_list = {
            args['material_name']: {
                'quantity': args['quantity'],
                'unit': args['unit']
            }
        }

        order = PurchaseOrder(
            manager_id=user_id,
            vendor_id=args['vendor_id'],
            material_list=material_list,
            status='pending'
        )

        db.session.add(order)
        db.session.commit()

        return {
            'message': 'Order created successfully',
            'order': order.to_dict()
        }, 201