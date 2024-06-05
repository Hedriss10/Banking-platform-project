from sqlalchemy import func
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash

from src import db 

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    user_identification = db.Column(db.Integer, unique=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150))
    type_user = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    created_on = db.Column(db.DateTime, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    points = db.relationship('Point', back_populates='user', lazy='dynamic')
    vacations = db.relationship('VocationBs', back_populates='user', lazy='dynamic')

    def __init__(self, user_identification, username, type_user, password, is_admin=False):
        self.user_identification = user_identification
        self.username = username
        self.type_user = type_user
        self.password = generate_password_hash(password)
        self.created_on = datetime.now()
        self.is_admin = is_admin
        
    def __repr__(self):
        return f"<ID {self.user_identification}>"