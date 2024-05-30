from sqlalchemy import func
from flask_login import UserMixin

from ..external import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_identification = db.Column(db.Integer, unique=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150))
    type_user = db.Column(db.String(100))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())