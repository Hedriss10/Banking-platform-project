from src.db.pg import Base

from sqlalchemy import (
    Column, Integer, String, Boolean, Text, DateTime, ForeignKey, func
)

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    cpf = Column(String(100), unique=True, nullable=True)
    username = Column(String(150), nullable=False)
    lastname = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False)
    password = Column(String(300), nullable=True)
    role = Column(String(200), nullable=True)
    typecontract = Column(String(30), nullable=False)
    session_token = Column(Text, nullable=True)
    is_admin = Column(Boolean, nullable=True)
    is_block = Column(Boolean, nullable=True)
    is_acctive = Column(Boolean, nullable=True)
    is_comission = Column(Boolean, nullable=True)
    create_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    is_first_acess = Column(Boolean, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=True)
    reset_password_at = Column(DateTime, nullable=True)
    reset_password_by = Column(Integer, nullable=True)
    action_reset_password_text = Column(Text, nullable=True)

class Role(Base):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=True)
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())
    updated_by = Column(Integer, nullable=True)
    deleted_by = Column(Integer, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=True)
