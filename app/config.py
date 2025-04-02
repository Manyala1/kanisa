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

    # Church Calendar API URL
    CHURCH_CALENDAR_API_URL = "http://calapi.inadiutorium.cz/api/v0/en/calendars/general-en"  # Base URL for Church Calendar API

    # API.Bible key
    API_BIBLE_KEY = os.getenv('API_BIBLE_KEY')  # Add your API.Bible key to the .env file