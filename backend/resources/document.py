from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.document import Document
from backend.models.user import User
from backend.models.purchase_order import PurchaseOrder
from backend import db
from werkzeug.datastructures import FileStorage
# from backend.services.cloudinary_service import cloudinary_service # Temporarily commented out

class DocumentResource(Resource):
    @jwt_required()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('order_id', type=int, required=True, help='Order ID is required')
        parser.add_argument('file', type=FileStorage, location='files', required=True, help='File is required')
        parser.add_argument('file_type', type=str, required=True, help='File type is required')
        args = parser.parse_args()

        user = User.query.get(get_jwt_identity())
        if not user:
            return {'message': 'User not found'}, 404

        order = PurchaseOrder.query.get(args['order_id'])
        if not order:
            return {'message': 'Order not found'}, 404

        if user.role.name == 'vendor' and order.vendor_id != user.id:
            return {'message': 'Access denied'}, 403
        if user.role.name == 'staff' and not any(assignment.staff_id == user.id for assignment in order.assignments):
            return {'message': 'Access denied'}, 403

        # uploaded_file_url = cloudinary_service.upload_file(args['file'].stream, folder="vendorsync_documents") # Temporarily commented out
        uploaded_file_url = "http://example.com/placeholder.pdf" # Placeholder for now

        if not uploaded_file_url:
            return {'message': 'Failed to upload file. Cloudinary integration is temporarily disabled.'}, 500

        document = Document(
            order_id=args['order_id'],
            file_url=uploaded_file_url,
            file_type=args['file_type'],
            uploaded_by=user.id
        )

        try:
            db.session.add(document)
            db.session.commit()
            return {
                'message': 'Document uploaded successfully',
                'document': {
                    'id': document.id,
                    'file_url': document.file_url,
                    'file_type': document.file_type,
                    'uploaded_by': document.uploaded_by,
                    'created_at': document.created_at.isoformat() if document.created_at else None
                }
            }, 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Failed to upload document: {str(e)}'}, 500

    @jwt_required()
    def get(self):
        user = User.query.get(get_jwt_identity())
        if not user:
            return {'message': 'User not found'}, 404

        parser = reqparse.RequestParser()
        parser.add_argument('order_id', type=int)
        args = parser.parse_args()

        if user.role.name == 'manager':
            query = Document.query.join(PurchaseOrder).filter(PurchaseOrder.manager_id == user.id)
        elif user.role.name == 'vendor':
            query = Document.query.join(PurchaseOrder).filter(PurchaseOrder.vendor_id == user.id)
        elif user.role.name == 'staff':
            query = Document.query.join(PurchaseOrder).join(OrderAssignment).filter(OrderAssignment.staff_id == user.id)
        else:
            return {'message': 'Access denied'}, 403

        if args['order_id']:
            query = query.filter_by(order_id=args['order_id'])

        documents = query.order_by(Document.created_at.desc()).all()

        return {
            'documents': [{
                'id': doc.id,
                'order_id': doc.order_id,
                'file_url': doc.file_url,
                'file_type': doc.file_type,
                'uploaded_by': doc.uploaded_by,
                'created_at': doc.created_at.isoformat() if doc.created_at else None
            } for doc in documents]
        }, 200