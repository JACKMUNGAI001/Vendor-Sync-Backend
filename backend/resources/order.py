from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.purchase_order import PurchaseOrder
from models.order_assignment import OrderAssignment
from models.user import User
from models.vendor import Vendor
from app import db
from sqlalchemy import or_, and_
from datetime import datetime

class OrderResource(Resource):
    @jwt_required()
    def get(self, id=None):
        """
        Get orders - role-based access
        - Managers: Their own orders
        - Staff: Orders assigned to them  
        - Vendors: Orders from them
        """
        user = User.query.get(get_jwt_identity())
        if not user:
            return {'message': 'User not found'}, 404
        
        # Get single order
        if id:
            order = PurchaseOrder.query.get(id)
            if not order:
                return {'message': 'Order not found'}, 404
            
            # Authorization checks
            if user.role.name == 'vendor' and order.vendor_id != user.id:
                return {'message': 'Access denied'}, 403
            if user.role.name == 'staff' and not any(assignment.staff_id == user.id for assignment in order.assignments):
                return {'message': 'Access denied'}, 403
            if user.role.name == 'manager' and order.manager_id != user.id:
                return {'message': 'Access denied'}, 403
            
            return order.to_dict(), 200
        
            # Get orders list with pagination
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default=1)
        parser.add_argument('per_page', type=int, default=10)
        parser.add_argument('status', type=str)
        args = parser.parse_args()

        # Role-based query filtering
        if user.role.name == 'manager':
            query = PurchaseOrder.query.filter_by(manager_id=user.id)
        elif user.role.name == 'staff':
            # Staff can see orders assigned to them
            query = PurchaseOrder.query.join(OrderAssignment).filter(
                OrderAssignment.staff_id == user.id
            )
        elif user.role.name == 'vendor':
            query = PurchaseOrder.query.filter_by(vendor_id=user.id)
        else:
            return {'message': 'Invalid role'}, 400