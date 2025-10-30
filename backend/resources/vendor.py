from flask_restful import Resource
from backend.models.vendor import Vendor

class VendorResource(Resource):
    def get(self):
        try:
            vendors = Vendor.query.filter_by(is_approved=True).all()
            return {
                'vendors': [vendor.to_dict() for vendor in vendors]
            }, 200
        except Exception as e:
            return {'message': f'Error fetching vendors: {str(e)}'}, 500