import cloudinary
import cloudinary.uploader
from flask import current_app

class CloudinaryService:
    def __init__(self):
        cloudinary.config(
            cloud_name=current_app.config['CLOUDINARY_CLOUD_NAME'],
            api_key=current_app.config['CLOUDINARY_API_KEY'],
            api_secret=current_app.config['CLOUDINARY_API_SECRET']
        )

    def upload_file(self, file_path, folder=None):
        try:
            options = {}
            if folder:
                options['folder'] = folder
            
            response = cloudinary.uploader.upload(file_path, **options)
            return response['secure_url']
        except Exception as e:
            print(f"Error uploading to Cloudinary: {e}")
            return None
