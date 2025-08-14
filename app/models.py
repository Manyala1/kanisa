from . import db
from flask_login import UserMixin
from datetime import datetime

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(150), nullable=False)

    events = db.relationship('Event', backref='created_by_admin', lazy=True)

    @property
    def is_admin(self):
        return True

    
class Member(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    zaq_number = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    jumuiya = db.Column(db.String(150), nullable=False)
    outstation = db.Column(db.String(150), nullable=False)
    center = db.Column(db.String(150), nullable=False)
    zone = db.Column(db.String(150), nullable=False)

    def get_id(self):
        return str(self.id)
    
    @property
    def is_admin(self):
        return False

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    theme = db.Column(db.String(150), nullable=False)
    involved = db.Column(db.String(150), nullable=False)
    venue = db.Column(db.String(150), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)