import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_secret_key_mad1_submision'
    
    # Database URI - using SQLite
    # This will create 'placement.db' in the 'instance' folder
    SQLALCHEMY_DATABASE_URI = 'sqlite:///placement.db'
    
    # Disable modification tracking to save memory
    SQLALCHEMY_TRACK_MODIFICATIONS = False
