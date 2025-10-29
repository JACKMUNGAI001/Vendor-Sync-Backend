from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.document import Document
from backend.models.user import User
from backend import db
import cloudinary
import cloudinary.uploader
from backend.config import Config

class DocumentResource(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role.name not in ['staff', 'vendor']:
            return {'message': 'Only staff and vendors can upload documents'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('order_id', type=int, required=True)
        parser.add_argument('file_type', required=True, choices=('invoice', 'receipt'))
        args = parser.parse_args()

        document = Document(
            order_id=args['order_id'],
            file_url=f"https://example.com/document_{args['order_id']}.pdf",
            file_type=args['file_type'],
            uploaded_by=user_id
        )

        db.session.add(document)
        db.session.commit()

        return {
            'message': 'Document uploaded successfully',
            'document': {
                'id': document.id,
                'file_url': document.file_url,
                'file_type': document.file_type,
                'order_id': document.order_id
            }
        }, 201