from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.db.database import db


class User(db.Model):
    __tablename__ = "user"
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    cpf: Mapped[str] = mapped_column(db.String(100), unique=True, nullable=True)
    username: Mapped[str] = mapped_column(db.String(150), nullable=False)
    lastname: Mapped[str] = mapped_column(db.String(150), nullable=False)
    email: Mapped[str] = mapped_column(db.String(150), nullable=False)
    password: Mapped[str] = mapped_column(db.String(300), nullable=True)
    role: Mapped[str] = mapped_column(db.String(200), nullable=True)
    typecontract: Mapped[str] = mapped_column(db.String(30), nullable=False)
    session_token: Mapped[str] = mapped_column(db.Text, nullable=True)
    is_admin: Mapped[bool] = mapped_column(db.Boolean, nullable=True)
    is_block: Mapped[bool] = mapped_column(db.Boolean, nullable=True)
    is_acctive: Mapped[bool] = mapped_column(db.Boolean, nullable=True)  
    is_comission: Mapped[bool] = mapped_column(db.Boolean, nullable=True)  
    create_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    is_first_acess: Mapped[bool] = mapped_column(db.Boolean, nullable=False)  
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, nullable=True, default=False)
    reset_password_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    reset_password_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    action_reset_password_text: Mapped[str] = mapped_column(db.Text, nullable=True)

    def __repr__(self):
        return f"<User: {self.username}>"

class Log(db.Model):
    __tablename__ = "logs"
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, server_default=func.now())
    logger_name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    level: Mapped[str] = mapped_column(db.String(100), nullable=False)
    message: Mapped[str] = mapped_column(db.Text, nullable=False)
    
    def __repr__(self):
        return f"<Log: Loggin registred at {self.timestamp} - {self.logger_name} - {self.level} - {self.message}>"

class Role(db.Model):
    __tablename__ = "role"
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(db.String(250), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, nullable=True, server_default='false')
    
    def __repr__(self):
        return f"<Role: {self.name}>"