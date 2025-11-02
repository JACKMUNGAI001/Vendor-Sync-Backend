from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.document import Document
from backend.models.user import User
from backend.models.vendor import Vendor
from backend.models.purchase_order import PurchaseOrder
from backend.models.order_assignment import OrderAssignment
from backend import db
from werkzeug.datastructures import FileStorage

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

        if user.role.name == 'vendor':
            vendor = Vendor.query.filter_by(email=user.email).first()
            if not vendor or order.vendor_id != vendor.id:
                return {'message': 'Access denied. You can only upload documents to your orders.'}, 403
        elif user.role.name == 'staff':
            if not any(assignment.staff_id == user.id for assignment in order.assignments):
                return {'message': 'Access denied. You can only upload documents to assigned orders.'}, 403
        elif user.role.name == 'manager':
            if order.manager_id != user.id:
                return {'message': 'Access denied. You can only upload documents to your orders.'}, 403
        else:
            return {'message': 'Access denied'}, 403

        valid_file_types = ['invoice', 'receipt', 'delivery_note', 'specification', 'contract', 'other']
        if args['file_type'] not in valid_file_types:
            return {
                'message': f'Invalid file type. Must be one of: {", ".join(valid_file_types)}'
            }, 400

        uploaded_file_url = f"https://placeholder.com/documents/{args['file'].filename}"

        if not uploaded_file_url:
            return {
                'message': 'Failed to upload file. Cloudinary integration is temporarily disabled.'
            }, 500

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
                'document': document.to_dict()
            }, 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Failed to upload document: {str(e)}'}, 500

    @jwt_required()
    def get(self, id=None):
        user = User.query.get(get_jwt_identity())
        if not user:
            return {'message': 'User not found'}, 404

        if id:
            document = Document.query.get(id)
            if not document:
                return {'message': 'Document not found'}, 404
            
            order = document.order
            
            if user.role.name == 'vendor':
                vendor = Vendor.query.filter_by(email=user.email).first()
                if not vendor or order.vendor_id != vendor.id:
                    return {'message': 'Access denied'}, 403
            elif user.role.name == 'staff':
                if not any(a.staff_id == user.id for a in order.assignments):
                    return {'message': 'Access denied'}, 403
            elif user.role.name == 'manager':
                if order.manager_id != user.id:
                    return {'message': 'Access denied'}, 403
            
            return document.to_dict(), 200

        parser = reqparse.RequestParser()
        parser.add_argument('order_id', type=int, location='args')
        parser.add_argument('file_type', type=str, location='args')
        parser.add_argument('page', type=int, default=1, location='args')
        parser.add_argument('per_page', type=int, default=10, location='args')
        args = parser.parse_args()

        if user.role.name == 'manager':
            query = Document.query.join(PurchaseOrder).filter(
                PurchaseOrder.manager_id == user.id
            )
        elif user.role.name == 'vendor':
            vendor = Vendor.query.filter_by(email=user.email).first()
            if not vendor:
                return {'documents': [], 'total': 0}, 200
            query = Document.query.join(PurchaseOrder).filter(
                PurchaseOrder.vendor_id == vendor.id
            )
        elif user.role.name == 'staff':
            query = Document.query.join(PurchaseOrder).join(OrderAssignment).filter(
                OrderAssignment.staff_id == user.id
            )
        else:
            return {'message': 'Access denied'}, 403

        if args['order_id']:
            query = query.filter(Document.order_id == args['order_id'])
        
        if args['file_type']:
            query = query.filter(Document.file_type == args['file_type'])

        pagination = query.order_by(Document.created_at.desc()).paginate(
            page=args['page'],
            per_page=args['per_page'],
            error_out=False
        )

        return {
            'documents': [doc.to_dict() for doc in pagination.items],
            'total_pages': pagination.pages,
            'current_page': pagination.page,
            'total_documents': pagination.total,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }, 200

    @jwt_required()
    def delete(self, id):
        user = User.query.get(get_jwt_identity())
        if not user:
            return {'message': 'User not found'}, 404

        document = Document.query.get(id)
        if not document:
            return {'message': 'Document not found'}, 404

        order = document.order

        if user.role.name == 'manager':
            if order.manager_id != user.id:
                return {'message': 'Access denied'}, 403
        elif document.uploaded_by != user.id:
            return {'message': 'You can only delete documents you uploaded'}, 403

        try:
            db.session.delete(document)
            db.session.commit()
            return {'message': 'Document deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Failed to delete document: {str(e)}'}, 500