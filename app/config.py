import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Ensure instance folder exists
    INSTANCE_PATH = os.path.join(os.getcwd(), 'instance')
    os.makedirs(INSTANCE_PATH, exist_ok=True)
    
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(32))
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        f'sqlite:///{os.path.join(INSTANCE_PATH, "db.sqlite3")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Additional security configurations
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True