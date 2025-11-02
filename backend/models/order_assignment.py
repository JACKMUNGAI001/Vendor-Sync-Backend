from backend.database import db

class OrderAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('purchase_order.id'))
    vendor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    assigned_at = db.Column(db.DateTime, server_default=db.func.now())
    status = db.Column(db.String(50), default='assigned')