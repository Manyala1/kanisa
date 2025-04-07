from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from os import path
from flask_login import LoginManager
from .config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Member, Admin 
    
    # Create the instance folder if it doesn't exist
    os.makedirs('instance', exist_ok=True)
    
    # Initialize database
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        # Try to load the user as a Member first, then as an Admin
        user = Member.query.get(int(id))
        if not user:
            user = Admin.query.get(int(id))
        return user

    return app