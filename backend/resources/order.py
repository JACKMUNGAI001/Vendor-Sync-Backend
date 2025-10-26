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