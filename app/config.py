import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = 'secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///kanisa.db'  # Use SQLite
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Additional security configurations
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True