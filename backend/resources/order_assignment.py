from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.order_assignment import OrderAssignment
from backend.models.purchase_order import PurchaseOrder
from backend.models.user import User
from backend import db

class OrderAssignmentResource(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role.name == 'staff':
            assignments = OrderAssignment.query.filter_by(staff_id=user.id).all()
        elif user.role.name == 'manager':
            assignments = OrderAssignment.query.all()
        else:
            return {'message': 'Access denied'}, 403
            
        return {'assignments': [assignment.to_dict() for assignment in assignments]}, 200

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role.name != 'manager':
            return {'message': 'Only managers can assign orders'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('order_id', type=int, required=True)
        parser.add_argument('staff_id', type=int, required=True)
        parser.add_argument('notes', type=str)
        args = parser.parse_args()

        order = PurchaseOrder.query.get(args['order_id'])
        if not order:
            return {'message': 'Order not found'}, 404

        staff = User.query.get(args['staff_id'])
        if not staff or staff.role.name != 'staff':
            return {'message': 'Invalid staff member'}, 400

        assignment = OrderAssignment(
            order_id=args['order_id'],
            staff_id=args['staff_id'],
            notes=args.get('notes')
        )

        db.session.add(assignment)
        db.session.commit()

        return {
            'message': 'Order assigned successfully',
            'assignment': assignment.to_dict()
        }, 201