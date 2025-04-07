# src/models/models.py
"""
    Models refatorando o projeto
    User -> ok
    Log -> ok
    Role -> ok
    Flag -> ok
    Rooms -> ok
    RoomsUsers -> ok
    Benefit -> ok
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
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
    
    # relacionamentos
    rooms = relationship("RoomsUsers", back_populates="user")

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


class Flag(db.Model):
    __tablename__ = "flags"
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(db.String(250), unique=True, nullable=True)
    rate: Mapped[float] = mapped_column(db.Float, default=0.0, nullable=True)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, nullable=True, server_default='false')
    created_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    
    def __repr__(self):
        return f"<Flag: {self.name}>"

class Rooms(db.Model):
    __tablename__ = "rooms"
    
    # Colunas
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    update_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True, onupdate=func.now())
    is_inactive: Mapped[bool] = mapped_column(Boolean, nullable=True)
    is_status: Mapped[bool] = mapped_column(Boolean, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=True)
    
    # Índice único
    __table_args__ = (
        UniqueConstraint('name', 'is_deleted', name='unique_rooms_name_is_deleted'),
    )
    
    # Relacionamentos
    users = relationship("RoomsUsers", back_populates="room")


class RoomsUsers(db.Model):
    __tablename__ = "rooms_users"
    
    # Colunas
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rooms_id: Mapped[int] = mapped_column(Integer, ForeignKey("rooms.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True, onupdate=func.now())
    is_inactive: Mapped[bool] = mapped_column(Boolean, nullable=True)
    is_status: Mapped[bool] = mapped_column(Boolean, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=True)
    
    # Constraint única e chaves estrangeiras
    __table_args__ = (
        UniqueConstraint('user_id', 'rooms_id', name='unique_user_room'),
    )

    room = relationship("Rooms", back_populates="users")
    user = relationship("User", back_populates="rooms")

class Benefit(db.Model):
    __tablename__ = "benefit"
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(db.String(250), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, nullable=True, server_default='false')
    
    def __repr__(self):
        return f"<Benefit: {self.name}>"


class Bank(db.Model):
    __tablename__ = "bank"
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(db.String(250), unique=True, nullable=True)
    id_bank: Mapped[int] = mapped_column(db.Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, nullable=True, server_default='false')
    
    def __repr__(self):
        return f"<Bank: {self.name}>"
    
    
class LoanOperation(db.Model):
    __tablename__ = "loan_operation"
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(db.String(250), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, nullable=True, server_default='false')
    
    def __repr__(self):
        return f"<LoanOperation: {self.name}>"
