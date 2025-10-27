from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.purchase_order import PurchaseOrder
from models.quote import Quote

class Dashboard(Resource):
    @jwt_required()
    def get(self):
        user = User.query.get(get_jwt_identity())
        data = []
        if user.role.name == 'manager':
            data = [{'id': o.id, 'description': f'Order #{o.id} - {o.status}'} for o in PurchaseOrder.query.filter_by(manager_id=user.id).all()]
        elif user.role.name == 'staff':
            data = [{'id': o.order.id, 'description': f'Order #{o.order.id} - {o.order.status}'} for o in user.assignments]
        elif user.role.name == 'vendor':
            data = [{'id': o.id, 'description': f'Order #{o.id} - {o.status}'} for o in PurchaseOrder.query.filter_by(vendor_id=user.id).all()]
        return data, 200