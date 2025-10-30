from backend import db

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_order'

    id = db.Column(db.Integer, primary_key=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    material_list = db.Column(db.JSON, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    delivery_date = db.Column(db.Date)
    special_instructions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    quotes = db.relationship('Quote', backref='order', foreign_keys='Quote.order_id')
    assignments = db.relationship('OrderAssignment', backref='order', foreign_keys='OrderAssignment.order_id')

    def to_dict(self):
        return {
            'id': self.id,
            'manager_id': self.manager_id,
            'vendor_id': self.vendor_id,
            'material_list': self.material_list,
            'status': self.status,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'special_instructions': self.special_instructions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'vendor_name': self.vendor.name if self.vendor else None,
            'manager_email': self.manager.email if self.manager else None
        }
    
    def __repr__(self):
        return f'<PurchaseOrder {self.id} - {self.status}>'