from backend import db
from flask import current_app
from sqlalchemy import event

class Requirement(db.Model):
    __tablename__ = 'requirement'

    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    specifications = db.Column(db.Text)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    manager = db.relationship('User', back_populates='requirements')

    __searchable__ = ['item_name', 'specifications']

    def to_dict(self):
        return {
            'objectID': self.id,
            'id': self.id,
            'item_name': self.item_name,
            'quantity': self.quantity,
            'specifications': self.specifications,
            'manager_id': self.manager_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<Requirement {self.item_name}>"

# Algolia Indexing Callbacks

def _get_algolia_service():
    from backend.services.algolia_service import algolia_service
    return algolia_service

@event.listens_for(Requirement, 'after_insert')
def new_requirement_to_algolia(mapper, connection, target):
    if current_app.config.get('ALGOLIA_ENABLED', False):
        _get_algolia_service().add_record(target.to_dict())

@event.listens_for(Requirement, 'after_update')
def update_requirement_in_algolia(mapper, connection, target):
    if current_app.config.get('ALGOLIA_ENABLED', False):
        _get_algolia_service().update_record(target.to_dict())

@event.listens_for(Requirement, 'after_delete')
def delete_requirement_from_algolia(mapper, connection, target):
    if current_app.config.get('ALGOLIA_ENABLED', False):
        _get_algolia_service().delete_record(target.id)