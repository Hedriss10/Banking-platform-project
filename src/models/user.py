from sqlalchemy import func
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash

from src import db 

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    user_identification = db.Column(db.String(100), unique=False)
    username = db.Column(db.String(150), unique=False, nullable=False)
    lastname = db.Column(db.String(150), unique=False, nullable=False)
    email= db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150))
    type_user_func = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_block = db.Column(db.Boolean, nullable=False, default=False)
    is_inactive = db.Column(db.Boolean, nullable=False, default=False)
    is_comission = db.Column(db.Boolean, nullable=False, default=False)
    extension = db.Column(db.String(100), nullable=False) # ramal
    extension_room = db.Column(db.String(100), nullable=False) # sala
    created_on = db.Column(db.DateTime, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    points = db.relationship('Point', back_populates='user', lazy='dynamic')
    vacations = db.relationship('VocationBs', back_populates='user', lazy='dynamic')

    def __init__(self, user_identification, username, 
                 lastname, email, type_user_func, password, extension,
                 extension_room, is_admin=False, is_block=False, 
                 is_inactive=False, is_comission=False):
        
        self.user_identification = user_identification
        self.username = username
        self.lastname = lastname
        self.email = email
        self.type_user_func = type_user_func
        self.password = generate_password_hash(password)
        self.extension = extension
        self.extension_room = extension_room
        self.created_on = datetime.now()
        self.is_admin = is_admin
        self.is_block = is_block
        self.is_inactive = is_inactive
        self.is_comission = is_comission
        
    def __repr__(self):
        return f"<ID {self.user_identification}>" 