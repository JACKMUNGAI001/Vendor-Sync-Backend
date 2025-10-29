from backend import db

class OrderAssignment(db.Model):
    __tablename__ = 'order_assignment'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('purchase_order.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, server_default=db.func.now())
    notes = db.Column(db.Text)

    order = db.relationship('PurchaseOrder', foreign_keys=[order_id])
    staff = db.relationship('User', foreign_keys=[staff_id])

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'staff_id': self.staff_id,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'notes': self.notes,
            'order_details': self.order.to_dict() if self.order else None,
            'staff_name': f"{self.staff.first_name} {self.staff.last_name}" if self.staff else None
        }