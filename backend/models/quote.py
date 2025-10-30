from backend import db
from flask import current_app
from sqlalchemy import event

class Quote(db.Model):
    __tablename__ = 'quote'

    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('purchase_order.id'), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    vendor = db.relationship('Vendor', back_populates='quotes')
    order = db.relationship('PurchaseOrder', back_populates='quotes')

    __searchable__ = ['notes', 'status']

    def to_dict(self):
        return {
            'objectID': self.id,
            'id': self.id,
            'vendor_id': self.vendor_id,
            'order_id': self.order_id,
            'price': float(self.price) if self.price else 0,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'vendor_name': self.vendor.name if self.vendor else None,
            'order_status': self.order.status if self.order else None
        }

    def __repr__(self):
        return f'<Quote {self.id} - ${self.price} - {self.status}>'

# Algolia Indexing Callbacks

def _get_algolia_service():
    from backend.services.algolia_service import algolia_service
    return algolia_service

@event.listens_for(Quote, 'after_insert')
def new_quote_to_algolia(mapper, connection, target):
    if current_app.config.get('ALGOLIA_ENABLED', False):
        _get_algolia_service().add_record(target.to_dict())

@event.listens_for(Quote, 'after_update')
def update_quote_in_algolia(mapper, connection, target):
    if current_app.config.get('ALGOLIA_ENABLED', False):
        _get_algolia_service().update_record(target.to_dict())

@event.listens_for(Quote, 'after_delete')
def delete_quote_from_algolia(mapper, connection, target):
    if current_app.config.get('ALGOLIA_ENABLED', False):
        _get_algolia_service().delete_record(target.id)