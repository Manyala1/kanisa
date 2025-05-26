import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret_key')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///kanisa.db'  
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Additional security configurations
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True

    # Universalis API Configuration
    UNIVERSALIS_API_URL = "https://universalis.com/api/v2"
    UNIVERSALIS_API_KEY = os.getenv('UNIVERSALIS_API_KEY')

    # Twilio Configuration
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

if __name__ == "__main__":
    print(f"UNIVERSALIS_API_KEY loaded: {'Yes' if Config.UNIVERSALIS_API_KEY else 'No'}")
    print(f"TWILIO_ACCOUNT_SID loaded: {'Yes' if Config.TWILIO_ACCOUNT_SID else 'No'}")