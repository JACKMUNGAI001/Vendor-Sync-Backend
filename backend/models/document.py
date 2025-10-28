from backend import db
from backend.models.user import User
from backend.models.purchase_order import PurchaseOrder

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('purchase_order.id'), nullable=False)
    file_url = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    order = db.relationship('PurchaseOrder', backref='documents')
    uploader = db.relationship('User', backref='documents')