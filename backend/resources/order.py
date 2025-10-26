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
        
        # Filter by status if provided
        if args['status']:
            query = query.filter_by(status=args['status'])

        # Pagination
        pagination = query.order_by(PurchaseOrder.created_at.desc()).paginate(
            page=args['page'], 
            per_page=args['per_page'],
            error_out=False
        )

        return {
            'orders': [order.to_dict() for order in pagination.items],
            'total_pages': pagination.pages,
            'current_page': pagination.page,
            'total_orders': pagination.total,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }, 200

    @jwt_required()
    def post(self):
        """Create a new purchase order (Manager only)"""
        user = User.query.get(get_jwt_identity())
        if not user or user.role.name != 'manager':
            return {'message': 'Only procurement managers can create orders'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('material_list', type=dict, required=True, help='Material list is required')
        parser.add_argument('vendor_id', type=int, required=True, help='Vendor ID is required')
        parser.add_argument('delivery_date', type=str)
        parser.add_argument('special_instructions', type=str)
        args = parser.parse_args()


        # Validate vendor exists
        vendor = Vendor.query.get(args['vendor_id'])
        if not vendor:
            return {'message': 'Vendor not found'}, 404

        # Validate material_list
        if not isinstance(args['material_list'], dict) or not args['material_list']:
            return {'message': 'Material list must be a non-empty object'}, 400

        # Parse delivery date
        delivery_date = None
        if args['delivery_date']:
            try:
                delivery_date = datetime.fromisoformat(args['delivery_date'].replace('Z', '+00:00'))
            except ValueError:
                return {'message': 'Invalid delivery date format'}, 400