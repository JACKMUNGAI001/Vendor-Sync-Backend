from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.user import User
from backend.models.purchase_order import PurchaseOrder
from backend.models.order_assignment import OrderAssignment
from backend.models.quote import Quote

class Dashboard(Resource):
    def get(self):
        print("Dashboard resource hit! (JWT temporarily disabled)")
        return {"message": "Dashboard data (dummy response)", "data": []}, 200