from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    zaq_number = db.Column(db.String(50), unique=True, nullable=False)
    jumuiya = db.Column(db.String(150), nullable=False)
    outstation = db.Column(db.String(150), nullable=False)
    center = db.Column(db.String(150), nullable=False)
    zone = db.Column(db.String(150), nullable=False)
    # Add relationships
    events = db.relationship('Event', backref='user', lazy=True)
    members = db.relationship('Member', backref='user', lazy=True)

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)  # Admin login uses email
    full_name = db.Column(db.String(150), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(150), nullable=False)  # Store hashed passwords
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())  # Track admin creation time

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    theme = db.Column(db.String(150), nullable=False)
    involved = db.Column(db.String(150), nullable=False)
    venue = db.Column(db.String(150), nullable=False)

class Member(db.Model, UserMixin):  # Inherit from UserMixin
    id = db.Column(db.Integer, primary_key=True)
    zaq_number = db.Column(db.String(50), unique=True, nullable=False)  
    full_name = db.Column(db.String(150), nullable=False)  
    phone_number = db.Column(db.String(20), nullable=False)  
    jumuiya = db.Column(db.String(150), nullable=False)
    outstation = db.Column(db.String(150), nullable=False)
    center = db.Column(db.String(150), nullable=False)
    zone = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Add foreign key
