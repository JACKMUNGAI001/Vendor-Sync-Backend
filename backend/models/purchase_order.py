from app import db
from models.user import User
from models.vendor import Vendor
from datetime import datetime

class PurchaseOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    material_list = db.Column(db.JSON, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    delivery_date = db.Column(db.Date)
    special_instructions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
    