from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.user import User
from backend.models.purchase_order import PurchaseOrder
from backend.models.quote import Quote

class Dashboard(Resource):
    @jwt_required()
    def get(self):
        """Return dashboard data based on the user's role."""
        user = User.query.get(get_jwt_identity())
        if not user:
            return {'message': 'User not found'}, 404

        data = []

        if user.role.name == 'manager':
            orders = PurchaseOrder.query.filter_by(manager_id=user.id).all()
            data = [
                {'id': o.id, 'description': f'Order #{o.id} - {o.status}'}
                for o in orders
            ]

        elif user.role.name == 'staff':
            data = [
                {'id': assignment.order.id, 'description': f'Order #{assignment.order.id} - {assignment.order.status}'}
                for assignment in user.assignments
            ]

        elif user.role.name == 'vendor':
            orders = PurchaseOrder.query.filter_by(vendor_id=user.id).all()
            data = [
                {'id': o.id, 'description': f'Order #{o.id} - {o.status}'}
                for o in orders
            ]

        else:
            return {'message': 'Invalid role'}, 403

        return data, 200
