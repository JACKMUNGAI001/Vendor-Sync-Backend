from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.user import User
from backend.models.purchase_order import PurchaseOrder
from backend.models.order_assignment import OrderAssignment
from backend.models.quote import Quote

class Dashboard(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        print(f"Dashboard resource hit! User ID: {user_id}")
        try:
            user = User.query.get(user_id)
            
            if not user:
                return {'message': 'User not found'}, 404