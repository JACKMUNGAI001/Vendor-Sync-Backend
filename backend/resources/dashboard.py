from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.user import User
from backend.models.purchase_order import PurchaseOrder
from backend.models.order_assignment import OrderAssignment
from backend.models.quote import Quote
from backend.models.requirement import Requirement
from backend.models.vendor import Vendor
from sqlalchemy import func

class Dashboard(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        print(f"Dashboard resource hit! User ID: {user_id}")
        
        user = User.query.get(user_id)
        
        if not user:
            return {'message': 'User not found'}, 404

        print(f"User role name: {user.role.name}")
        print(f"User role ID: {user.role_id}")

        try:
            if user.role.name == 'manager':
                return self._get_manager_dashboard(user)
            elif user.role.name == 'staff':
                return self._get_staff_dashboard(user)
            elif user.role.name == 'vendor':
                return self._get_vendor_dashboard(user)
            else:
                return {'message': 'Invalid role'}, 400

        except Exception as e:
            print(f"Dashboard error: {str(e)}")
            return {'message': f'Server error: {str(e)}'}, 500

    def _get_manager_dashboard(self, user):
        total_orders = PurchaseOrder.query.filter_by(manager_id=user.id).count()
        pending_orders = PurchaseOrder.query.filter_by(manager_id=user.id, status='pending').count()
        completed_orders = PurchaseOrder.query.filter_by(manager_id=user.id, status='completed').count()
        
        total_requirements = Requirement.query.filter_by(manager_id=user.id).count()
        pending_quotes = Quote.query.join(PurchaseOrder).filter(
            PurchaseOrder.manager_id == user.id,
            Quote.status == 'pending'
        ).count()

        recent_orders = PurchaseOrder.query.filter_by(manager_id=user.id)\
            .order_by(PurchaseOrder.created_at.desc()).limit(5).all()

        pending_quotes_list = Quote.query.join(PurchaseOrder).filter(
            PurchaseOrder.manager_id == user.id,
            Quote.status == 'pending'
        ).order_by(Quote.created_at.desc()).limit(5).all()

        data = {
            'role': 'manager',
            'statistics': {
                'total_orders': total_orders,
                'pending_orders': pending_orders,
                'completed_orders': completed_orders,
                'total_requirements': total_requirements,
                'pending_quotes': pending_quotes
            },
            'recent_orders': [{
                'id': order.id,
                'order_number': order.order_number,
                'status': order.status,
                'vendor_id': order.vendor_id,
                'created_at': order.created_at.isoformat() if order.created_at else None
            } for order in recent_orders],
            'pending_quotes': [{
                'id': quote.id,
                'order_id': quote.order_id,
                'vendor_id': quote.vendor_id,
                'price': float(quote.price) if quote.price else 0,
                'created_at': quote.created_at.isoformat() if quote.created_at else None
            } for quote in pending_quotes_list]
        }

        print(f"Manager dashboard data: {data}")
        return data, 200

    def _get_staff_dashboard(self, user):
        assignments = OrderAssignment.query.filter_by(staff_id=user.id)\
            .order_by(OrderAssignment.assigned_at.desc()).all()

        total_assignments = len(assignments)
        active_assignments = sum(1 for a in assignments if a.order.status not in ['completed', 'cancelled'])

        data = {
            'role': 'staff',
            'statistics': {
                'total_assignments': total_assignments,
                'active_assignments': active_assignments
            },
            'assignments': [{
                'id': assignment.id,
                'order_id': assignment.order.id,
                'order_number': assignment.order.order_number,
                'order_status': assignment.order.status,
                'assigned_at': assignment.assigned_at.isoformat() if assignment.assigned_at else None,
                'status': assignment.status
            } for assignment in assignments]
        }

        print(f"Staff dashboard data: {data}")
        return data, 200

    def _get_vendor_dashboard(self, user):
        vendor = Vendor.query.filter_by(email=user.email).first()
        
        if not vendor:
            return {
                'role': 'vendor',
                'message': 'Vendor profile not found. Please contact administrator.',
                'statistics': {
                    'is_verified': False,
                    'total_orders': 0,
                    'total_quotes': 0,
                    'pending_quotes': 0,
                    'accepted_quotes': 0
                },
                'orders': [],
                'quotes': []
            }, 200

        orders = PurchaseOrder.query.filter_by(vendor_id=vendor.id)\
            .order_by(PurchaseOrder.created_at.desc()).all()

        quotes = Quote.query.filter_by(vendor_id=vendor.id)\
            .order_by(Quote.created_at.desc()).all()

        pending_quotes_count = sum(1 for q in quotes if q.status == 'pending')
        accepted_quotes_count = sum(1 for q in quotes if q.status == 'accepted')

        data = {
            'role': 'vendor',
            'vendor_info': {
                'id': vendor.id,
                'name': vendor.name,
                'company_name': vendor.company_name,
                'is_verified': vendor.is_verified
            },
            'statistics': {
                'is_verified': vendor.is_verified,
                'total_orders': len(orders),
                'total_quotes': len(quotes),
                'pending_quotes': pending_quotes_count,
                'accepted_quotes': accepted_quotes_count
            },
            'orders': [{
                'id': order.id,
                'order_number': order.order_number,
                'status': order.status,
                'created_at': order.created_at.isoformat() if order.created_at else None
            } for order in orders[:5]],
            'quotes': [{
                'id': quote.id,
                'order_id': quote.order_id,
                'price': float(quote.price) if quote.price else 0,
                'status': quote.status,
                'created_at': quote.created_at.isoformat() if quote.created_at else None
            } for quote in quotes[:5]]
        }

        print(f"Vendor dashboard data: {data}")
        return data, 200