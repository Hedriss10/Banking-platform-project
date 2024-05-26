from external import db
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_identification = db.Column(db.Integer, unique=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    type_user = db.Column(db.String(100), primary_key=True)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())