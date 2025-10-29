from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.purchase_order import PurchaseOrder
from backend.models.vendor import Vendor
from backend.models.user import User
from backend.models.order_assignment import OrderAssignment
from backend import db

class OrderResource(Resource):
    @jwt_required()
    def get(self, id=None):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if id:
            order = PurchaseOrder.query.get(id)
            if not order:
                return {'message': 'Order not found'}, 404
            
            # Authorization
            if user.role.name == 'vendor' and order.vendor_id != user.id:
                return {'message': 'Access denied'}, 403
            if user.role.name == 'staff' and not OrderAssignment.query.filter_by(order_id=id, staff_id=user.id).first():
                return {'message': 'Access denied'}, 403
                
            return order.to_dict(), 200
        
        # Get orders based on role
        if user.role.name == 'manager':
            orders = PurchaseOrder.query.filter_by(manager_id=user.id).all()
        elif user.role.name == 'staff':
            assignments = OrderAssignment.query.filter_by(staff_id=user.id).all()
            orders = [assignment.order for assignment in assignments]
        elif user.role.name == 'vendor':
            vendor = Vendor.query.filter_by(contact_email=user.email).first()
            orders = PurchaseOrder.query.filter_by(vendor_id=vendor.id).all() if vendor else []
        else:
            return {'message': 'Invalid role'}, 400
            
        return {'orders': [order.to_dict() for order in orders]}, 200

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role.name != 'manager':
            return {'message': 'Only managers can create orders'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('vendor_id', type=int, required=True)
        parser.add_argument('material_name', required=True)
        parser.add_argument('quantity', type=int, required=True)
        parser.add_argument('unit', required=True)
        parser.add_argument('specifications', type=str)
        args = parser.parse_args()

        vendor = Vendor.query.get(args['vendor_id'])
        if not vendor:
            return {'message': 'Vendor not found'}, 404

        material_list = {
            args['material_name']: {
                'quantity': args['quantity'],
                'unit': args['unit'],
                'specifications': args.get('specifications', '')
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

    @jwt_required()
    def patch(self, id):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        order = PurchaseOrder.query.get(id)
        if not order:
            return {'message': 'Order not found'}, 404

        # Authorization
        if user.role.name == 'vendor' and order.vendor_id != user.id:
            return {'message': 'Access denied'}, 403
        if user.role.name == 'staff' and not OrderAssignment.query.filter_by(order_id=id, staff_id=user.id).first():
            return {'message': 'Access denied'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('status', type=str)
        args = parser.parse_args()

        if args.get('status'):
            valid_statuses = ['pending', 'ordered', 'in_progress', 'delivered', 'completed', 'cancelled']
            if args['status'] not in valid_statuses:
                return {'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}, 400
            order.status = args['status']

        db.session.commit()

        return {
            'message': 'Order updated successfully',
            'order': order.to_dict()
        }, 200