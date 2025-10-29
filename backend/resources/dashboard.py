from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.user import User
from backend.models.purchase_order import PurchaseOrder
from backend.models.order_assignment import OrderAssignment

class Dashboard(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return {'message': 'User not found'}, 404

        data = []
        role_name = user.role.name if user.role else 'unknown'

        try:
            if role_name == 'manager':
                orders = PurchaseOrder.query.filter_by(manager_id=user.id).all()
                data = [
                    {'id': order.id, 'description': f'Order #{order.id} - {order.status}'}
                    for order in orders
                ]

            elif role_name == 'staff':
                assignments = OrderAssignment.query.filter_by(staff_id=user.id).all()
                data = [
                    {'id': assignment.order.id, 'description': f'Assigned Order #{assignment.order.id} - {assignment.order.status}'}
                    for assignment in assignments
                    if assignment.order
                ]

            elif role_name == 'vendor':
                orders = PurchaseOrder.query.filter_by(vendor_id=user.id).all()
                data = [
                    {'id': order.id, 'description': f'Vendor Order #{order.id} - {order.status}'}
                    for order in orders
                ]

            else:
                return {'message': f'Unknown role: {role_name}'}, 400

            return data, 200

        except Exception as e:
            return {'message': f'Error fetching dashboard data: {str(e)}'}, 500