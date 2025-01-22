from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from src import db

class Employee(db.Model):
    __tablename__ = 'employee'

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_pis = Column(String(255), nullable=False)
    matricula = Column(String(255), nullable=False)
    empresa = Column(String(255), nullable=False)
    situacao_cadastro = Column(String(50), default='ativo')
    carga_horaria_semanal = Column(Integer, default=44)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, nullable=True)
    updated_by = Column(Integer, nullable=True)
    deleted_by = Column(Integer, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)

    user = relationship("User", back_populates="employees")
