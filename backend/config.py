import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///vendorsync.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-super-secret-jwt-key-here')
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    
    # Algolia Configuration
    ALGOLIA_ENABLED = os.getenv('ALGOLIA_ENABLED', 'False').lower() == 'true'
    ALGOLIA_APP_ID = os.getenv('ALGOLIA_APP_ID', '')
    ALGOLIA_API_KEY = os.getenv('ALGOLIA_API_KEY', '')
    
    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME', '')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY', '')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET', '')
    
    # SendGrid Configuration
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')