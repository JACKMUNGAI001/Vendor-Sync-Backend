from backend import db
from sqlalchemy import UniqueConstraint, event
from flask import current_app

class Vendor(db.Model):
    __tablename__ = 'vendor'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    company_name = db.Column(db.String(255))
    contact_person = db.Column(db.String(255))
    is_verified = db.Column(db.Boolean, default=False)
    category_id = db.Column(db.Integer, db.ForeignKey('vendor_category.id'), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    quotes = db.relationship('Quote', back_populates='vendor', cascade='all, delete-orphan')
    category = db.relationship('VendorCategory', back_populates='vendors')

    __table_args__ = (UniqueConstraint('email', name='_vendor_email_uc'),)

    __searchable__ = ['name', 'email', 'company_name', 'contact_person']

    def to_dict(self):
        return {
            'objectID': self.id,
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'company_name': self.company_name,
            'contact_person': self.contact_person,
            'is_verified': self.is_verified,
            'category_id': self.category_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<Vendor {self.name}>"

# Algolia Indexing Callbacks

def _get_algolia_service():
    from backend.services.algolia_service import algolia_service
    return algolia_service

@event.listens_for(Vendor, 'after_insert')
def new_vendor_to_algolia(mapper, connection, target):
    if current_app.config.get('ALGOLIA_ENABLED', False):
        _get_algolia_service().add_record(target.to_dict())

@event.listens_for(Vendor, 'after_update')
def update_vendor_in_algolia(mapper, connection, target):
    if current_app.config.get('ALGOLIA_ENABLED', False):
        _get_algolia_service().update_record(target.to_dict())

@event.listens_for(Vendor, 'after_delete')
def delete_vendor_from_algolia(mapper, connection, target):
    if current_app.config.get('ALGOLIA_ENABLED', False):
        _get_algolia_service().delete_record(target.id)