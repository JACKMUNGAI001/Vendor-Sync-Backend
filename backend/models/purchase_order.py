from backend import db

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_order'

    id = db.Column(db.Integer, primary_key=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    material_list = db.Column(db.JSON, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    manager = db.relationship('User', foreign_keys=[manager_id])
    vendor = db.relationship('Vendor', foreign_keys=[vendor_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'manager_id': self.manager_id,
            'vendor_id': self.vendor_id,
            'material_list': self.material_list,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'vendor_name': self.vendor.name if self.vendor else None
        }