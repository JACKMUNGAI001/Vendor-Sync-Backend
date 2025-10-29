from backend import db

class Vendor(db.Model):
    __tablename__ = 'vendor'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    contact_email = db.Column(db.String(255), unique=True, nullable=False)
    contact_phone = db.Column(db.String(20))
    business_type = db.Column(db.String(100))
    description = db.Column(db.Text)
    is_approved = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'business_type': self.business_type,
            'description': self.description,
            'is_approved': self.is_approved
        }