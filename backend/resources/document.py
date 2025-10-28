from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
import cloudinary
import cloudinary.uploader
import time

from backend.models.document import Document
from backend.models.user import User
from backend.models.purchase_order import PurchaseOrder
from backend import db
from backend.config import Config


class DocumentResource(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return {'message': 'User not found'}, 404

        if user.role.name not in ['staff', 'vendor']:
            return {'message': 'Unauthorized'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('order_id', type=int, required=True, help='Order ID is required')
        parser.add_argument('file_type', type=str, required=True, help='File type is required')
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

        signature = cloudinary.utils.api_sign_request(
            params_to_sign=params,
            api_secret=Config.CLOUDINARY_API_SECRET
        )

        upload_url = f"https://api.cloudinary.com/v1_1/{Config.CLOUDINARY_CLOUD_NAME}/auto/upload"

        return {
            'upload_url': upload_url,
            'timestamp': timestamp,
            'signature': signature,
            'upload_preset': 'vendorsync_preset',
            'folder': 'vendorsync',
            'api_key': Config.CLOUDINARY_API_KEY
        }, 200
