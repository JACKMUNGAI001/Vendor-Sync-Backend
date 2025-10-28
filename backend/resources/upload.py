from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.document import Document
from backend.models.user import User
from backend.models.purchase_order import PurchaseOrder
from backend import db
import cloudinary.uploader
from backend.config import Config

class UploadResource(Resource):
    @jwt_required()
    def post(self):
        user = User.query.get(get_jwt_identity())
        if user.role.name not in ['staff', 'vendor']:
            return {'message': 'Unauthorized'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('file', type='file', location='files', required=True)
        parser.add_argument('order_id', type=int, location='form', required=True)
        parser.add_argument('file_type', type=str, location='form', required=True)
        args = parser.parse_args()

        order = PurchaseOrder.query.get(args['order_id'])
        if not order:
            return {'message': 'Order not found'}, 404

        # Upload to Cloudinary
        try:
            upload_result = cloudinary.uploader.upload(
                args['file'],
                folder='vendorsync',
                resource_type='auto'
            )
        except Exception as e:
            return {'message': 'Cloudinary upload failed'}, 500

        # Save document record
        document = Document(
            order_id=args['order_id'],
            file_url=upload_result['secure_url'],
            file_type=args['file_type'],
            uploaded_by=user.id,
            public_id=upload_result['public_id']
        )
        db.session.add(document)
        db.session.commit()

        return {
            'message': 'File uploaded',
            'document_id': document.id,
            'file_url': document.file_url
        }, 201