from backend.database import db

class PurchaseOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    budget = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, server_default=db.func.now())