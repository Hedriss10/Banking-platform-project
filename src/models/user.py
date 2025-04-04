from sqlalchemy.sql import func

from src.db.database import db


class User(db.Model):
    
    __tablename__ = "user"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cpf = db.Column(db.String(100), unique=True, nullable=True)
    username = db.Column(db.String(150), nullable=False)
    lastname = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(300), nullable=True)
    role = db.Column(db.String(200), nullable=True)
    typecontract = db.Column(db.String(30), nullable=False)
    session_token = db.Column(db.Text, nullable=True)
    is_admin = db.Column(db.Boolean, nullable=True)
    is_block = db.Column(db.Boolean, nullable=True)
    is_acctive = db.Column(db.Boolean, nullable=True)
    is_comission = db.Column(db.Boolean, nullable=True)
    create_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    is_first_acess = db.Column(db.Boolean, nullable=False)
    is_deleted = db.Column(db.Boolean, nullable=True, default=False)
    reset_password_at = db.Column(db.DateTime, nullable=True)
    reset_password_by = db.Column(db.Integer, nullable=True)
    action_reset_password_text = db.Column(db.Text, nullable=True)


    def __repr__(self):
        return f"<User {self.username}>"
