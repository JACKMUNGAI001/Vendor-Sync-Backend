import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/vendorsync')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-super-secret-jwt-key-here')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    
    # Algolia Configuration
    ALGOLIA_APP_ID = 'NUF1223K4R'
    ALGOLIA_API_KEY = '0ba760722de94835fbcc6eda8b20d872'
    
    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME = 'Root'  # Usually the cloud name, not 'Root'
    CLOUDINARY_API_KEY = '178465286397512'
    CLOUDINARY_API_SECRET = 'xV9o3HTECbymyVRCOdb16JnT7F'
    
    # SendGrid Configuration
    SENDGRID_API_KEY = 'SG.KmgUmljzTKO8NKDCXDX_UQ.j42'
