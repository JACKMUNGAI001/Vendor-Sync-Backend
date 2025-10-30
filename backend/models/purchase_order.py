from backend import db
from flask import current_app
from sqlalchemy import event

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_order'

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(50), default='pending')
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Deferred import to avoid circular dependency
    manager = db.relationship(
        lambda: __import__('backend.models.user', fromlist=['User']).User,
        back_populates='managed_orders',
        foreign_keys=[manager_id]
    )

    vendor = db.relationship(
        lambda: __import__('backend.models.vendor', fromlist=['Vendor']).Vendor
    )

    quotes = db.relationship(
        lambda: __import__('backend.models.quote', fromlist=['Quote']).Quote,
        back_populates='order',
        cascade='all, delete-orphan'
    )
    documents = db.relationship(
        lambda: __import__('backend.models.document', fromlist=['Document']).Document,
        back_populates='order',
        cascade='all, delete-orphan'
    )

    assignments = db.relationship(
        lambda: __import__('backend.models.order_assignment', fromlist=['OrderAssignment']).OrderAssignment,
        back_populates='order',
        cascade='all, delete-orphan'
    )

    __searchable__ = ['order_number', 'status']

    def to_dict(self):
        return {
            'objectID': self.id,
            'id': self.id,
            'order_number': self.order_number,
            'status': self.status,
            'manager_id': self.manager_id,
            'vendor_id': self.vendor_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<PurchaseOrder {self.order_number}>"

# Algolia Indexing Callbacks

def _get_algolia_service():
    from backend.services.algolia_service import algolia_service
    return algolia_service

@event.listens_for(PurchaseOrder, 'after_insert')
def new_purchase_order_to_algolia(mapper, connection, target):
    if current_app.config.get('ALGOLIA_ENABLED', False):
        _get_algolia_service().add_record(target.to_dict())

@event.listens_for(PurchaseOrder, 'after_update')
def update_purchase_order_in_algolia(mapper, connection, target):
    if current_app.config.get('ALGOLIA_ENABLED', False):
        _get_algolia_service().update_record(target.to_dict())

@event.listens_for(PurchaseOrder, 'after_delete')
def delete_purchase_order_from_algolia(mapper, connection, target):
    if current_app.config.get('ALGOLIA_ENABLED', False):
        _get_algolia_service().delete_record(target.id)
