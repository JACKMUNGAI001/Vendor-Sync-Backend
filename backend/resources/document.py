from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.document import Document
from models.user import User
from models.purchase_order import PurchaseOrder
from app import db
import cloudinary
import cloudinary.uploader
from config import Config
import time

class DocumentUploadResource(Resource):
    @jwt_required()
    def post(self):
        user = User.query.get(get_jwt_identity())
        if user.role.name not in ['staff', 'vendor']:
            return {'message': 'Unauthorized'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('order_id', type=int, required=True)
        parser.add_argument('file_type', type=str, required=True)
        args = parser.parse_args()

        order = PurchaseOrder.query.get(args['order_id'])
        if not order:
            return {'message': 'Order not found'}, 404

        timestamp = int(time.time())
        params = {
            'timestamp': timestamp,
            'upload_preset': 'vendorsync_preset',
            'folder': 'vendorsync'
        }

        params_to_sign = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        signature = cloudinary.utils.api_sign_request(
            params,
            Config.CLOUDINARY_API_SECRET
        )

        return {
            'upload_url': 'https://api.cloudinary.com/v1_1/' + Config.CLOUDINARY_CLOUD_NAME + '/auto/upload',
            'timestamp': timestamp,
            'signature': signature,
            'upload_preset': 'vendorsync_preset',
            'folder': 'vendorsync',
            'api_key': Config.CLOUDINARY_API_KEY
        }, 200