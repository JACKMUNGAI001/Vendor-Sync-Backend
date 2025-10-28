from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.purchase_order import PurchaseOrder
from backend.models.order_assignment import OrderAssignment
from backend.models.user import User
from backend.models.vendor import Vendor
from backend.app import db
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
            

            # Create order
        order = PurchaseOrder(
            manager_id=user.id,
            vendor_id=args['vendor_id'],
            material_list=args['material_list'],
            status='pending',
            delivery_date=delivery_date,
            special_instructions=args['special_instructions']
        )

        try:
            db.session.add(order)
            db.session.commit()
            return {
                'message': 'Order created successfully',
                'order': order.to_dict()
            }, 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Failed to create order: {str(e)}'}, 500

    @jwt_required()
    def patch(self, id):
        """Update order (status updates and other fields)"""
        user = User.query.get(get_jwt_identity())
        if not user:
            return {'message': 'User not found'}, 404

        order = PurchaseOrder.query.get(id)
        if not order:
            return {'message': 'Order not found'}, 404
        

        # Authorization checks for status updates
        if user.role.name == 'staff':
            # Staff can only update status if assigned to the order
            if not any(assignment.staff_id == user.id for assignment in order.assignments):
                return {'message': 'Not assigned to this order'}, 403
        elif user.role.name == 'vendor':
            # Vendors can only update their own orders
            if order.vendor_id != user.id:
                return {'message': 'Access denied'}, 403
        elif user.role.name != 'manager':
            return {'message': 'Unauthorized'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('status', type=str)
        parser.add_argument('special_instructions', type=str)
        parser.add_argument('delivery_date', type=str)
        args = parser.parse_args()

        # Update fields
        if args['status']:
            valid_statuses = ['pending', 'ordered', 'delivered', 'inspected', 'completed', 'cancelled']
            if args['status'] not in valid_statuses:
                return {'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}, 400
            order.status = args['status']

        if args['special_instructions'] is not None:
            order.special_instructions = args['special_instructions']

        if args['delivery_date']:
            try:
                order.delivery_date = datetime.fromisoformat(args['delivery_date'].replace('Z', '+00:00'))
            except ValueError:
                return {'message': 'Invalid delivery date format'}, 400

        try:
            db.session.commit()
            return {
                'message': 'Order updated successfully',
                'order': order.to_dict()
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Failed to update order: {str(e)}'}, 500
        

    @jwt_required()
    def delete(self, id):
        """Delete order (Manager only)"""
        user = User.query.get(get_jwt_identity())
        if not user or user.role.name != 'manager':
            return {'message': 'Only procurement managers can delete orders'}, 403

        order = PurchaseOrder.query.get(id)
        if not order:
            return {'message': 'Order not found'}, 404

        # Managers can only delete their own orders
        if order.manager_id != user.id:
            return {'message': 'Can only delete your own orders'}, 403

        # Prevent deletion of orders that are already in progress
        if order.status not in ['pending', 'cancelled']:
            return {'message': 'Cannot delete orders that are in progress or completed'}, 400

        try:
            # Delete related assignments first
            OrderAssignment.query.filter_by(order_id=id).delete()
            db.session.delete(order)
            db.session.commit()
            return {'message': 'Order deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Failed to delete order: {str(e)}'}, 500
            
class OrderVendorResource(Resource):
    @jwt_required()
    def get(self):
        """Get orders for vendor (Vendor only)"""
        user = User.query.get(get_jwt_identity())
        if not user or user.role.name != 'vendor':
            return {'message': 'Access denied. Vendor role required.'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default=1)
        parser.add_argument('per_page', type=int, default=10)
        parser.add_argument('status', type=str)
        args = parser.parse_args()

        # Query orders for this vendor
        query = PurchaseOrder.query.filter_by(vendor_id=user.id)
        
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
    

class OrderAssignmentResource(Resource):
    @jwt_required()
    def post(self):
        """Assign order to staff (Manager only)"""
        user = User.query.get(get_jwt_identity())
        if not user or user.role.name != 'manager':
            return {'message': 'Only procurement managers can assign orders'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('order_id', type=int, required=True, help='Order ID is required')
        parser.add_argument('staff_id', type=int, required=True, help='Staff ID is required')
        parser.add_argument('notes', type=str)
        args = parser.parse_args()

        # Validate order exists and belongs to this manager
        order = PurchaseOrder.query.get(args['order_id'])
        if not order or order.manager_id != user.id:
            return {'message': 'Order not found or access denied'}, 404

        # Validate staff exists and has staff role
        staff = User.query.get(args['staff_id'])
        if not staff or staff.role.name != 'staff':
            return {'message': 'Invalid staff member'}, 400

        # Check if assignment already exists
        existing_assignment = OrderAssignment.query.filter_by(
            order_id=args['order_id'], 
            staff_id=args['staff_id']
        ).first()
        if existing_assignment:
            return {'message': 'Order already assigned to this staff member'}, 400

        # Create assignment
        assignment = OrderAssignment(
            order_id=args['order_id'],
            staff_id=args['staff_id'],
            notes=args['notes']
        )

        try:
            db.session.add(assignment)
            db.session.commit()
            return {
                'message': 'Order assigned successfully',
                'assignment': assignment.to_dict()
            }, 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Failed to assign order: {str(e)}'}, 500
        
    @jwt_required()
    def get(self):
        """Get order assignments"""
        user = User.query.get(get_jwt_identity())
        if not user:
            return {'message': 'User not found'}, 404

        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default=1)
        parser.add_argument('per_page', type=int, default=10)
        args = parser.parse_args()

        if user.role.name == 'manager':
            # Managers can see all assignments for their orders
            query = OrderAssignment.query.join(PurchaseOrder).filter(
                PurchaseOrder.manager_id == user.id
            )
        elif user.role.name == 'staff':
            # Staff can see their own assignments
            query = OrderAssignment.query.filter_by(staff_id=user.id)
        else:
            return {'message': 'Access denied'}, 403

        pagination = query.order_by(OrderAssignment.assigned_at.desc()).paginate(
            page=args['page'], 
            per_page=args['per_page'],
            error_out=False
        )

        return {
            'assignments': [assignment.to_dict() for assignment in pagination.items],
            'total_pages': pagination.pages,
            'current_page': pagination.page,
            'total_assignments': pagination.total,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }, 200

    @jwt_required()
    def delete(self, assignment_id):
        """Remove order assignment (Manager only)"""
        user = User.query.get(get_jwt_identity())
        if not user or user.role.name != 'manager':
            return {'message': 'Only procurement managers can remove assignments'}, 403

        assignment = OrderAssignment.query.get(assignment_id)
        if not assignment:
            return {'message': 'Assignment not found'}, 404

        # Verify the order belongs to this manager
        order = PurchaseOrder.query.get(assignment.order_id)
        if not order or order.manager_id != user.id:
            return {'message': 'Access denied'}, 403

        try:
            db.session.delete(assignment)
            db.session.commit()
            return {'message': 'Assignment removed successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Failed to remove assignment: {str(e)}'}, 500

