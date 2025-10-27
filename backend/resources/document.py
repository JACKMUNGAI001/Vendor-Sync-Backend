from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.document import Document
from models.user import User
from models.purchase_order import PurchaseOrder
from app import db
import cloudinary.uploader
from config import Config

class DocumentResource(Resource):
    @jwt_required()
    def post(self):
        user = User.query.get(get_jwt_identity())
        if user.role.name not in ['staff', 'vendor']:
            return {'message': 'Unauthorized'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('order_id', type=int, required=True)
        parser.add_argument('file', type=str, required=True)
        parser.add_argument('file_type', required=True)
        args = parser.parse_args()

        order = PurchaseOrder.query.get(args['order_id'])
        if not order:
            return {'message': 'Order not found'}, 404

        upload_result = cloudinary.uploader.upload(args['file'], resource_type='auto')
        document = Document(
            order_id=args['order_id'],
            file_url=upload_result['secure_url'],
            file_type=args['file_type'],
            uploaded_by=user.id
        )
        db.session.add(document)
        db.session.commit()
        return {'message': 'Document uploaded'}, 201