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

    CATHOLIC_DAILY_READINGS_API_URL = "https://catholic-daily-readings-api-url.com/api/readings/today"  # Replace with the actual API URL
    CHURCH_CALENDAR_API_URL = "https://church-calendar-api-url.com/api/readings/today"  # Replace with the correct API URL