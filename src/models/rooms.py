from sqlalchemy import func
from flask_login import UserMixin
from src import db 
from src.models.user import User



room_user_association = db.Table(
    'room_user_association',
    db.Column('room_id', db.Integer, db.ForeignKey('rooms.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class Roomns(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    create_room = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    users = db.relationship('User', secondary='room_user_association', backref='rooms')