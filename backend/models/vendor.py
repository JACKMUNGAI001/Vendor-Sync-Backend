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

        def to_dict(self):
        """Convert vendor object to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code,
            'business_type': self.business_type,
            'description': self.description,
            'is_approved': self.is_approved,
            'tax_id': self.tax_id,
            'payment_terms': self.payment_terms,
            'rating': self.rating,
            'total_orders': self.total_orders,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_dict_public(self):
        """Return vendor data for public viewing (without sensitive info)"""
        return {
            'id': self.id,
            'name': self.name,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'business_type': self.business_type,
            'description': self.description,
            'rating': self.rating,
            'total_orders': self.total_orders,
            'is_approved': self.is_approved
        }
    