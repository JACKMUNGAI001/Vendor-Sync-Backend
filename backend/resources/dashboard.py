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

            data = []

            if user.role.name == 'manager':
                orders = PurchaseOrder.query.filter_by(manager_id=user.id).all()
                data = [
                    {
                        'id': order.id, 
                        'description': f'Order #{order.id} - {order.status}',
                        'type': 'order',
                        'status': order.status,
                        'created_at': order.created_at.isoformat() if order.created_at else None
                    }
                    for order in orders
                ]

            elif user.role.name == 'staff':
                assignments = OrderAssignment.query.filter_by(staff_id=user.id).all()
                data = [
                    {
                        'id': assignment.order.id,
                        'description': f'Assigned Order #{assignment.order.id} - {assignment.order.status}',
                        'type': 'assignment', 
                        'status': assignment.order.status,
                        'assigned_at': assignment.assigned_at.isoformat() if assignment.assigned_at else None
                    }
                    for assignment in assignments
                ]

            elif user.role.name == 'vendor':
                orders = PurchaseOrder.query.filter_by(vendor_id=user.id).all()
                quotes = Quote.query.filter_by(vendor_id=user.id).all()
                
                order_data = [
                    {
                        'id': order.id,
                        'description': f'Order #{order.id}',
                        'type': 'order',
                        'status': order.status
                    }
                    for order in orders
                ]
                
                quote_data = [
                    {
                        'id': quote.id,
                        'description': f'Quote #{quote.id}',
                        'type': 'quote', 
                        'status': quote.status,
                        'price': float(quote.price) if quote.price else 0
                    }
                    for quote in quotes
                ]
                
                data = order_data + quote_data

            else:
                return {'message': 'Invalid role'}, 400

            print(f"Dashboard data returned: {data}")
            return data, 200

        except Exception as e:
            return {'message': f'Server error: {str(e)}'}, 500