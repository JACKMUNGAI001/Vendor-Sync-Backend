from app import db
from models.user import User
from models.purchase_order import PurchaseOrder

class OrderAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('purchase_order.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, server_default=db.func.now())
    notes = db.Column(db.Text)

    # Relationships
    order = db.relationship('PurchaseOrder', backref='assignments')
    staff = db.relationship('User', backref='assigned_orders')
    
    __table_args__ = (db.UniqueConstraint('order_id', 'staff_id', name='unique_order_staff'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'staff_id': self.staff_id,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'notes': self.notes,
            'staff_email': self.staff.email if self.staff else None,
            'order_status': self.order.status if self.order else None
        }
    
    def __repr__(self):
        return f'<OrderAssignment Order:{self.order_id} Staff:{self.staff_id}>'
    