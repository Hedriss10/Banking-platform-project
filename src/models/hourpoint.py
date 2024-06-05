from datetime import datetime
from flask_login import UserMixin
from src import db
from src.models.user import User

class Point(db.Model, UserMixin):
    __tablename__ = 'point'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    day_hour = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    type = db.Column(db.String(50), nullable=False)

    user = db.relationship('User', back_populates='points')

    def __repr__(self):
        return f'<Point {self.id} {self.type} at {self.day_hour}>'
    
class VocationBs(db.Model, UserMixin):
    __tablename__ = 'vocationbs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', back_populates='vacations')

    def __repr__(self):
        return f'<Vacation {self.id} from {self.start_date} to {self.end_date}>'

