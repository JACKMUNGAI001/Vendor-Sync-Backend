from backend import db

class VendorCategory(db.Model):
    __tablename__ = 'vendor_category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    vendors = db.relationship('Vendor', back_populates='category')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

    def __repr__(self):
        return f"<VendorCategory {self.name}>"
