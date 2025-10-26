from app import db

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    contact_email = db.Column(db.String(255), unique=True, nullable=False)
    contact_phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100), default='USA')
    postal_code = db.Column(db.String(20))
    business_type = db.Column(db.String(100))  # e.g., 'Construction Materials', 'Equipment Rental'
    description = db.Column(db.Text)
    is_approved = db.Column(db.Boolean, default=False)
    tax_id = db.Column(db.String(100))  # Business tax ID/EIN
    payment_terms = db.Column(db.String(100), default='Net 30')
    rating = db.Column(db.Float, default=0.0)  # Average rating from orders
    total_orders = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())