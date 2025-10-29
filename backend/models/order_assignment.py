from backend import db

class OrderAssignment(db.Model):
    __tablename__ = 'order_assignment'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('purchase_order.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, server_default=db.func.now())
    notes = db.Column(db.Text)

    __table_args__ = (db.UniqueConstraint('order_id', 'staff_id', name='unique_order_staff'),)
    
    order = db.relationship('PurchaseOrder', foreign_keys=[order_id])
    staff = db.relationship('User', foreign_keys=[staff_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'staff_id': self.staff_id,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'notes': self.notes
        }
    
    def __repr__(self):
        return f'<OrderAssignment Order:{self.order_id} Staff:{self.staff_id}>'