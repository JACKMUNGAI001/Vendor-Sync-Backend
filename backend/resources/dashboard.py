from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.user import User
from backend.models.purchase_order import PurchaseOrder
from backend.models.order_assignment import OrderAssignment
from backend.models.quote import Quote
from backend.models.vendor import Vendor

class Dashboard(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return {'message': 'User not found'}, 404

        data = {
            'user': user.to_dict(),
            'stats': {},
            'recent_activity': []
        }

        if user.role.name == 'manager':
            orders = PurchaseOrder.query.filter_by(manager_id=user.id).all()
            quotes = Quote.query.all()
            
            data['stats'] = {
                'total_orders': len(orders),
                'pending_orders': len([o for o in orders if o.status == 'pending']),
                'total_quotes': len(quotes),
                'pending_quotes': len([q for q in quotes if q.status == 'pending'])
            }
            
            data['recent_activity'] = [
                {
                    'id': order.id,
                    'type': 'order',
                    'description': f'Order #{order.id} - {order.status}',
                    'status': order.status,
                    'created_at': order.created_at.isoformat() if order.created_at else None
                }
                for order in orders[:5]  # Last 5 orders
            ]

        elif user.role.name == 'staff':
            assignments = OrderAssignment.query.filter_by(staff_id=user.id).all()
            orders = [assignment.order for assignment in assignments]
            
            data['stats'] = {
                'assigned_orders': len(assignments),
                'in_progress': len([o for o in orders if o.status == 'in_progress']),
                'completed': len([o for o in orders if o.status == 'completed'])
            }
            
            data['recent_activity'] = [
                {
                    'id': assignment.order.id,
                    'type': 'assignment',
                    'description': f'Assigned Order #{assignment.order.id}',
                    'status': assignment.order.status,
                    'assigned_at': assignment.assigned_at.isoformat() if assignment.assigned_at else None
                }
                for assignment in assignments[:5]
            ]

        elif user.role.name == 'vendor':
            vendor = Vendor.query.filter_by(contact_email=user.email).first()
            if vendor:
                orders = PurchaseOrder.query.filter_by(vendor_id=vendor.id).all()
                quotes = Quote.query.filter_by(vendor_id=vendor.id).all()
                
                data['stats'] = {
                    'total_orders': len(orders),
                    'pending_quotes': len([q for q in quotes if q.status == 'pending']),
                    'accepted_quotes': len([q for q in quotes if q.status == 'accepted'])
                }
                
                order_activity = [
                    {
                        'id': order.id,
                        'type': 'order',
                        'description': f'Order #{order.id} - {order.status}',
                        'status': order.status
                    }
                    for order in orders[:3]
                ]
                
                quote_activity = [
                    {
                        'id': quote.id,
                        'type': 'quote',
                        'description': f'Quote #{quote.id} - ${quote.price} - {quote.status}',
                        'status': quote.status
                    }
                    for quote in quotes[:2]
                ]
                
                data['recent_activity'] = order_activity + quote_activity

        return data, 200