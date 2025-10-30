from backend import db

class OrderAssignment(db.Model):
    __tablename__ = 'order_assignment'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('purchase_order.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, server_default=db.func.now())
    status = db.Column(db.String(50), default='assigned')

    # Deferred imports
    staff = db.relationship(
        lambda: __import__('backend.models.user', fromlist=['User']).User,
        back_populates='assignments',
        foreign_keys=[staff_id]
    )
    order = db.relationship(
        lambda: __import__('backend.models.purchase_order', fromlist=['PurchaseOrder']).PurchaseOrder,
        back_populates='assignments'
    )

    def __repr__(self):
        return f"<OrderAssignment order_id={self.order_id} staff_id={self.staff_id}>"
