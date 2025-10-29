import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///vendorsync.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-super-secret-jwt-key-here')
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    
    # Algolia Configuration
    ALGOLIA_APP_ID = 'NUF1223K4R'
    ALGOLIA_API_KEY = '0ba760722de94835fbcc6eda8b20d872'
    
    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME = 'demo'
    CLOUDINARY_API_KEY = 'demo'
    CLOUDINARY_API_SECRET = 'demo'
    
    # SendGrid Configuration
    SENDGRID_API_KEY = 'demo'