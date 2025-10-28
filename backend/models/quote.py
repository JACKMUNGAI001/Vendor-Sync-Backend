from backend.app import db
from backend.models.vendor import Vendor
from backend.models.purchase_order import PurchaseOrder

class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('purchase_order.id'), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    vendor = db.relationship('Vendor', backref='quotes')
    order = db.relationship('PurchaseOrder', backref='quotes')
