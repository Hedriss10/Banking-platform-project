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
    typecontract = db.Column(db.String(30), nullable=False) 
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_block = db.Column(db.Boolean, nullable=False, default=False)
    is_inactive = db.Column(db.Boolean, nullable=False, default=False)
    is_comission = db.Column(db.Boolean, nullable=False, default=False)
    extension = db.Column(db.String(100), nullable=False)  # ramal
    extension_room = db.Column(db.String(100), nullable=False)  # sala
    created_on = db.Column(db.DateTime, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    
    # relationship
    points = db.relationship('Point', back_populates='user', lazy='dynamic')
    vacations = db.relationship('VocationBs', back_populates='user', lazy='dynamic')
    permissions = db.relationship('UserPermission', backref='user', lazy='dynamic')

    def __init__(self, user_identification, username, 
                 lastname, email, type_user_func, typecontract, password, extension,
                 extension_room, is_admin=False, is_block=False, 
                 is_inactive=False, is_comission=False):
        
        self.user_identification = user_identification
        self.username = username
        self.lastname = lastname
        self.email = email
        self.type_user_func = type_user_func
        self.typecontract =  typecontract
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

class Permission(db.Model):
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    users = db.relationship('UserPermission', backref='permission', lazy='dynamic')
    
    def __repr__(self):
        return f"<Permission {self.name}>"

class UserPermission(db.Model):
    __tablename__ = 'user_permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), nullable=False)
    
    def __repr__(self):
        return f"<UserPermission User: {self.user_id}, Permission: {self.permission_id}>"