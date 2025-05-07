import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = 'secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///kanisa.db'  
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Additional security configurations
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True

    # Church Calendar API URL
    CHURCH_CALENDAR_API_URL = "http://calapi.inadiutorium.cz/api/v0/en/calendars/general-en" 

    # API.Bible key
    API_BIBLE_KEY = os.getenv('API_BIBLE_KEY')
    
    class config:
        TWILIO_ACCOUNT_SID = "ACa6b2e8cc89212dc5a7d29bbb20964f5e"
        TWILIO_ACCOUNT_SID = "e08c0380135eb6305e311cc463a6ac24"
        TWILIO_PHONE_NUMBER = "+19207648987"