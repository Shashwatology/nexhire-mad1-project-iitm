import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_secret_key_mad1_submision'
    
    # Check if running on Vercel (read-only file system except /tmp)
    if os.environ.get('VERCEL') == '1':
        SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/placement.db'
    else:
        # Local development database
        SQLALCHEMY_DATABASE_URI = 'sqlite:///placement.db'
    
    # Disable modification tracking to save memory
    SQLALCHEMY_TRACK_MODIFICATIONS = False
