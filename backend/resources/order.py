from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.purchase_order import PurchaseOrder
from backend.models.order_assignment import OrderAssignment
from backend.models.user import User
from backend.models.vendor import Vendor
from backend import db
from datetime import datetime

class OrderResource(Resource):
    @jwt_required()
    def get(self, id=None):
        user = User.query.get(get_jwt_identity())
        if not user:
            return {'message': 'User not found'}, 404
        
        if id:
            order = PurchaseOrder.query.get(id)
            if not order:
                return {'message': 'Order not found'}, 404
            
            if user.role.name == 'vendor':
                vendor = Vendor.query.filter_by(email=user.email).first()
                if not vendor or order.vendor_id != vendor.id:
                    return {'message': 'Access denied'}, 403
            elif user.role.name == 'staff':
                if not any(assignment.staff_id == user.id for assignment in order.assignments):
                    return {'message': 'Access denied'}, 403
            elif user.role.name == 'manager':
                if order.manager_id != user.id:
                    return {'message': 'Access denied'}, 403
            
            return order.to_dict(), 200
        
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default=1, location='args')
        parser.add_argument('per_page', type=int, default=10, location='args')
        parser.add_argument('status', type=str, location='args')
        args = parser.parse_args()

        if user.role.name == 'manager':
            query = PurchaseOrder.query.filter_by(manager_id=user.id)
        elif user.role.name == 'staff':
            query = PurchaseOrder.query.join(OrderAssignment).filter(
                OrderAssignment.staff_id == user.id
            )
        elif user.role.name == 'vendor':
            vendor = Vendor.query.filter_by(email=user.email).first()
            if not vendor:
                return {'orders': [], 'total_pages': 0, 'current_page': 1, 'total_orders': 0}, 200
            query = PurchaseOrder.query.filter_by(vendor_id=vendor.id)
        else:
            return {'message': 'Invalid role'}, 400
        
        if args['status']:
            query = query.filter_by(status=args['status'])

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
        user = User.query.get(get_jwt_identity())
        if not user or user.role.name != 'manager':
            return {'message': 'Only procurement managers can create orders'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('order_number', type=str, required=True, help='Order number is required')
        parser.add_argument('vendor_id', type=int, required=True, help='Vendor ID is required')
        parser.add_argument('requirement_id', type=int)
        args = parser.parse_args()

        if PurchaseOrder.query.filter_by(order_number=args['order_number']).first():
            return {'message': 'Order number already exists'}, 400

        vendor = Vendor.query.get(args['vendor_id'])
        if not vendor:
            return {'message': 'Vendor not found'}, 404
        
        if not vendor.is_verified:
            return {'message': 'Cannot create order for unverified vendor'}, 400

        order = PurchaseOrder(
            order_number=args['order_number'],
            manager_id=user.id,
            vendor_id=args['vendor_id'],
            status='pending'
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
        user = User.query.get(get_jwt_identity())
        if not user:
            return {'message': 'User not found'}, 404

        order = PurchaseOrder.query.get(id)
        if not order:
            return {'message': 'Order not found'}, 404

        if user.role.name == 'staff':
            if not any(assignment.staff_id == user.id for assignment in order.assignments):
                return {'message': 'Not assigned to this order'}, 403
        elif user.role.name == 'vendor':
            vendor = Vendor.query.filter_by(email=user.email).first()
            if not vendor or order.vendor_id != vendor.id:
                return {'message': 'Access denied'}, 403
        elif user.role.name == 'manager':
            if order.manager_id != user.id:
                return {'message': 'Access denied'}, 403
        else:
            return {'message': 'Unauthorized'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('status', type=str)
        args = parser.parse_args()

        if args['status']:
            valid_statuses = ['pending', 'ordered', 'delivered', 'inspected', 'completed', 'cancelled']
            if args['status'] not in valid_statuses:
                return {'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}, 400
            
            old_status = order.status
            order.status = args['status']

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
        user = User.query.get(get_jwt_identity())
        if not user or user.role.name != 'manager':
            return {'message': 'Only procurement managers can delete orders'}, 403

        order = PurchaseOrder.query.get(id)
        if not order:
            return {'message': 'Order not found'}, 404

        if order.manager_id != user.id:
            return {'message': 'Can only delete your own orders'}, 403

        if order.status not in ['pending', 'cancelled']:
            return {'message': 'Cannot delete orders that are in progress or completed'}, 400

        try:
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
        user = User.query.get(get_jwt_identity())
        if not user or user.role.name != 'vendor':
            return {'message': 'Access denied. Vendor role required.'}, 403

        vendor = Vendor.query.filter_by(email=user.email).first()
        if not vendor:
            return {'message': 'Vendor profile not found'}, 404

        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default=1, location='args')
        parser.add_argument('per_page', type=int, default=10, location='args')
        parser.add_argument('status', type=str, location='args')
        args = parser.parse_args()

        query = PurchaseOrder.query.filter_by(vendor_id=vendor.id)
        
        if args['status']:
            query = query.filter_by(status=args['status'])

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
        user = User.query.get(get_jwt_identity())
        if not user or user.role.name != 'manager':
            return {'message': 'Only procurement managers can assign orders'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('order_id', type=int, required=True, help='Order ID is required')
        parser.add_argument('staff_id', type=int, required=True, help='Staff ID is required')
        parser.add_argument('notes', type=str)
        args = parser.parse_args()

        order = PurchaseOrder.query.get(args['order_id'])
        if not order or order.manager_id != user.id:
            return {'message': 'Order not found or access denied'}, 404

        staff = User.query.get(args['staff_id'])
        if not staff or staff.role.name != 'staff':
            return {'message': 'Invalid staff member'}, 400

        existing_assignment = OrderAssignment.query.filter_by(
            order_id=args['order_id'], 
            staff_id=args['staff_id']
        ).first()
        if existing_assignment:
            return {'message': 'Order already assigned to this staff member'}, 400

        assignment = OrderAssignment(
            order_id=args['order_id'],
            staff_id=args['staff_id'],
            status='assigned'
        )

        try:
            db.session.add(assignment)
            db.session.commit()

            return {
                'message': 'Order assigned successfully',
                'assignment': {
                    'id': assignment.id,
                    'order_id': assignment.order_id,
                    'staff_id': assignment.staff_id,
                    'status': assignment.status,
                    'assigned_at': assignment.assigned_at.isoformat() if assignment.assigned_at else None
                }
            }, 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Failed to assign order: {str(e)}'}, 500
        
    @jwt_required()
    def get(self):
        user = User.query.get(get_jwt_identity())
        if not user:
            return {'message': 'User not found'}, 404

        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default=1, location='args')
        parser.add_argument('per_page', type=int, default=10, location='args')
        args = parser.parse_args()

        if user.role.name == 'manager':
            query = OrderAssignment.query.join(PurchaseOrder).filter(
                PurchaseOrder.manager_id == user.id
            )
        elif user.role.name == 'staff':
            query = OrderAssignment.query.filter_by(staff_id=user.id)
        else:
            return {'message': 'Access denied'}, 403

        pagination = query.order_by(OrderAssignment.assigned_at.desc()).paginate(
            page=args['page'], 
            per_page=args['per_page'],
            error_out=False
        )

        return {
            'assignments': [{
                'id': a.id,
                'order_id': a.order_id,
                'staff_id': a.staff_id,
                'status': a.status,
                'assigned_at': a.assigned_at.isoformat() if a.assigned_at else None,
                'order': {
                    'order_number': a.order.order_number,
                    'status': a.order.status
                }
            } for a in pagination.items],
            'total_pages': pagination.pages,
            'current_page': pagination.page,
            'total_assignments': pagination.total,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }, 200

    @jwt_required()
    def delete(self, assignment_id):
        user = User.query.get(get_jwt_identity())
        if not user or user.role.name != 'manager':
            return {'message': 'Only procurement managers can remove assignments'}, 403

        assignment = OrderAssignment.query.get(assignment_id)
        if not assignment:
            return {'message': 'Assignment not found'}, 404

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