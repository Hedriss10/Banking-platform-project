# src/models/models.py
## TODO - falta o manager dos pagamentos
## TODO - falta o manager das estatisticas 
## TODO - falta o dashboard
## TODO - Desenvolvimento do banco de horas 


import decimal
import enum
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.db.database import db


class User(db.Model):
    __tablename__ = "user"
    __table_args__ = {'schema': 'public'}
    
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


class OptionRegister(enum.Enum):
    ATIVO = 'ativo'
    INATIVO = 'inativo'
    SUSPENSO = 'suspenso' 
    
    @classmethod
    def get_valid_values(cls):
        return [e.value for e in cls]


class Employee(db.Model):
    __tablename__ = "employee"
    __table_args__ = {'schema': 'time_recording'}

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    numero_pis: Mapped[str] = mapped_column(db.CHAR(20), nullable=False, unique=True, comment="Número do PIS/PASEP (11 dígitos)")
    matricula: Mapped[str] = mapped_column(db.String(50), nullable=False, unique=True)
    company_id: Mapped[int] = mapped_column(db.Integer, ForeignKey("time_recording.company.id"), nullable=False)
    situacao_cadastro: Mapped[str] = mapped_column(db.String(20),  nullable=False, server_default="ativo")
    carga_horaria_semanal: Mapped[float] = mapped_column(db.Numeric(5, 2), nullable=False, server_default="44.0")
    user_id: Mapped[int] = mapped_column(db.Integer, ForeignKey("public.user.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, server_default=func.current_db.DateTime())
    created_by: Mapped[int] = mapped_column(db.Integer, ForeignKey("public.user.id"), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, ForeignKey("public.user.id"), nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, ForeignKey("public.user.id"), nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, nullable=False, server_default="false")

    def __repr__(self):
        return f"<Employee: {self.matricula}>"


class Company(db.Model):
    __tablename__ = "company"
    __table_args__ = {'schema': 'time_recording'}

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    cpnj: Mapped[str] = mapped_column(db.String(14), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, nullable=False, server_default="false")

    def __repr__(self):
        return f"<Company: {self.cpnj}>"


class Log(db.Model):
    __tablename__ = "logs"
    __table_args__ = {'schema': 'audit_logs'}
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, server_default=func.now())
    logger_name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    level: Mapped[str] = mapped_column(db.String(100), nullable=False)
    message: Mapped[str] = mapped_column(db.Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, server_default=func.now())
    
    def __repr__(self):
        return f"<Log: Loggin registred at {self.timestamp} - {self.logger_name} - {self.level} - {self.message}>"


class Role(db.Model):
    __tablename__ = "role"
    __table_args__ = {'schema': 'public'}
    
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
    __table_args__ = {'schema': 'public'}
    
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
    __table_args__ = {'schema': 'public'}
    
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
    __table_args__ = {'schema': 'public'}
    
    # Colunas
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rooms_id: Mapped[int] = mapped_column(Integer, ForeignKey("rooms.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("public.user.id"), nullable=False)
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
    __table_args__ = {'schema': 'public'}
    
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
    __table_args__ = {'schema': 'public'}
    
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
    __table_args__ = {'schema': 'public'}
    
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
    
    
class Bankers(db.Model):
    __tablename__ = "bankers"
    __table_args__ = {'schema': 'public'}
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(db.String(250), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, nullable=True, server_default='false')
    
    __table_args__ = (
        UniqueConstraint('name', 'is_deleted', name='unique_name_bankers'),
    )
    
    
    def __repr__(self):
        return f"<Bankers: {self.name}>"
    
    
class FinancialAgreements(db.Model):
    __tablename__ = "financial_agreements"
    __table_args__ = {'schema': 'public'}
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(db.String(250), unique=True, nullable=True)
    banker_id: Mapped[int] = mapped_column(db.Integer, ForeignKey("public.bankers.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, nullable=True, server_default='false')
    
    def __repr__(self):
        return f"<FinancialAgreements: {self.name}>"


class TablesFinance(db.Model):
    __tablename__ = "tables_finance"
    __table_args__ = {'schema': 'public'}
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(db.String(250), unique=True, nullable=True)
    type_table: Mapped[str] = mapped_column(db.String(250), nullable=True)
    table_code: Mapped[str] = mapped_column(db.String(250), nullable=True)
    start_term: Mapped[str] = mapped_column(db.String(250), nullable=True)
    end_term: Mapped[str] = mapped_column(db.String(250), nullable=True)
    rate: Mapped[float] = mapped_column(db.Float, nullable=True)
    is_status: Mapped[bool] = mapped_column(db.Boolean, nullable=True, server_default='false')
    financial_agreements_id: Mapped[int] = mapped_column(db.Integer, ForeignKey("public.financial_agreements.id"), nullable=False)
    issue_date: Mapped[str] = mapped_column(db.String(250), nullable=True)
    start_rate: Mapped[str] = mapped_column(db.String(250), nullable=True)
    end_rate: Mapped[str] = mapped_column(db.String(250), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, nullable=True, server_default='false')
    created_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, server_default=func.now())
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f"<TablesFinance: {self.name}>"
    

class ObtianReport(db.Model):
    # TODO - falta implementar o export de pagamentos para os vendedores
    __talbename__ = "obtian_report"
    __table_args__ = {'schema': 'public'}
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    name_report: Mapped[str] = mapped_column(db.String(20), unique=True, nullable=False)
    name_customer: Mapped[str] = mapped_column(db.String(50), unique=True, nullable=False)
    cpf: Mapped[str] = mapped_column(db.String(250), nullable=True)
    number_proposal: Mapped[str] = mapped_column(db.String(250), nullable=True)
    table_code: Mapped[str] = mapped_column(db.String(250), nullable=True)
    flat: Mapped[float] = mapped_column(db.Float, default=0.0, nullable=True)
    value_operation: Mapped[str] = mapped_column(db.String(250), nullable=True)
    is_validated: Mapped[bool] = mapped_column(db.Boolean, nullable=True, server_default='false')
    user_id: Mapped[int] = mapped_column(db.Integer, ForeignKey("public.user.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, nullable=True, server_default='false')
    

    def __repr__(self):
        return f"<Report: {self.name_report}>"


class Proposal(db.Model):
    __tablename__ = "proposal"
    __table_args__ = {'schema': 'public'}
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(db.String(100), unique=True, nullable=True)
    data_nascimento: Mapped[str] = mapped_column(db.DateTime, nullable=True)
    genero: Mapped[str] = mapped_column(db.String(20), nullable=True)
    email: Mapped[str] = mapped_column(db.String(100), nullable=True)
    cpf: Mapped[str] = mapped_column(db.String(20), nullable=True)
    rg_documento: Mapped[str] = mapped_column(db.String(20), nullable=True)
    naturalidade: Mapped[str] = mapped_column(db.String(100), nullable=True)
    cidade_naturalidade: Mapped[str] = mapped_column(db.String(100), nullable=True)
    uf_naturalidade: Mapped[str] = mapped_column(db.String(100), nullable=True)
    orgao_emissor: Mapped[str] = mapped_column(db.String(100), nullable=True)
    uf_emissor: Mapped[str] = mapped_column(db.String(2), nullable=True)
    nome_mae: Mapped[str] = mapped_column(db.String(100), nullable=True)
    nome_pai: Mapped[str] = mapped_column(db.String(100), nullable=True)
    bairro: Mapped[str] = mapped_column(db.String(100), nullable=True)
    endereco: Mapped[str] = mapped_column(db.String(100), nullable=True)
    numero_endereco: Mapped[str] = mapped_column(db.String(100), nullable=True)
    complemento_endereco: Mapped[str] = mapped_column(db.String(100), nullable=True)
    cidade: Mapped[str] = mapped_column(db.String(100), nullable=True)
    valor_salario: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=True)
    salario_liquido: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=True)
    telefone: Mapped[str] = mapped_column(db.String(100), nullable=True)
    telefone_residencial: Mapped[str] = mapped_column(db.String(100), nullable=True)
    telefone_comercial: Mapped[str] = mapped_column(db.String(100), nullable=True)
    data_emissao: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    cep: Mapped[str] = mapped_column(db.String(100), nullable=True)
    uf_cidade: Mapped[str] = mapped_column(db.String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, nullable=True, server_default='false')
    user_id: Mapped[int] = mapped_column(db.Integer, ForeignKey("public.user.id"), nullable=False)
    
    def __repr__(self):
        return f"<Proposal: {self.id}>"

class ProposalBenenift(db.Model):
    __tablename__ = "proposal_benefit"
    __table_args__ = {'schema': 'public'}
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    proposal_id: Mapped[int] = mapped_column(db.Integer, ForeignKey("public.proposal.id"), nullable=False)
    benefit_id: Mapped[int] = mapped_column(db.Integer, ForeignKey("public.benefit.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, nullable=True, server_default='false')
    
    def __repr__(self):
        return f"<ProposalBenenift: {self.id}>"

class ProposalLoan(db.Model):
    __tablename__ = "proposal_loan"
    __table_args__ = {'schema': 'public'}
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    proposal_id: Mapped[int] = mapped_column(db.Integer, ForeignKey("public.proposal.id"), nullable=False)
    loan_operation_id: Mapped[int] = mapped_column(db.Integer, ForeignKey("public.loan_operation.id"), nullable=False)
    senha_servidor: Mapped[str] = mapped_column(db.String(40), nullable=False)
    matricula: Mapped[str] = mapped_column(db.String(40), nullable=False)
    data_dispacho: Mapped[datetime] = mapped_column(db.DateTime, nullable=False)
    margem: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    prazo_inicio: Mapped[int] = mapped_column(db.Integer, nullable=False)
    prazo_fim: Mapped[int] = mapped_column(db.Integer, nullable=False)
    valor_operacao: Mapped[float] = mapped_column(db.Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, nullable=True, server_default='false')
    user_id: Mapped[int] = mapped_column(db.Integer, ForeignKey("public.user.id"), nullable=False)
    financial_agreements_id: Mapped[int] = mapped_column(db.Integer, ForeignKey("public.financial_agreements.id"), nullable=False)
    tables_finance_id: Mapped[int] = mapped_column(db.Integer, ForeignKey("public.tables_finance.id"), nullable=False)
    
    def __repr__(self):
        return f"<ProposalLoan: {self.id}>"
    
class ProposalStatus(db.Model):
    __tablename__ = "proposal_status"
    __table_args__ = {'schema': 'public'}
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    aguardando_digitacao: Mapped[bool] = mapped_column(db.Boolean, nullable=False, default=False)
    pendente_digitacao: Mapped[bool] = mapped_column(db.Boolean, nullable=False, default=False)
    contrato_em_digitacao: Mapped[bool] = mapped_column(db.Boolean, nullable=False, default=False)
    aceite_feito_analise_banco: Mapped[bool] = mapped_column(db.Boolean, nullable=False, default=False)
    contrato_pendente_banco: Mapped[bool] = mapped_column(db.Boolean, nullable=False, default=False)
    aguardando_pagamento: Mapped[bool] = mapped_column(db.Boolean, nullable=False, default=False)
    contrato_pago: Mapped[bool] = mapped_column(db.Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, nullable=True, server_default='false')
    user_id: Mapped[int] = mapped_column(db.Integer, ForeignKey("public.user.id"), nullable=False)
    proposal_id: Mapped[int] = mapped_column(db.Integer, ForeignKey("public.proposal.id"), nullable=False)
    action_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    action_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    
    def __repr__(self):
        return f"<ProposalStatus: {self.id}>"

class ProposalWallet(db.Model):
    __tablename__ = "proposal_wallet"
    __table_args__ = {'schema': 'public'}
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    agencia_banco: Mapped[str] = mapped_column(db.String(100), nullable=False)
    pix_chave: Mapped[str] = mapped_column(db.String(120), nullable=False)
    numero_conta: Mapped[str] = mapped_column(db.String(20), nullable=False)
    agencia_dv: Mapped[str] = mapped_column(db.String(10), nullable=False)
    agencia_op: Mapped[str] = mapped_column(db.String(10), nullable=False)
    agency_dvop: Mapped[str] = mapped_column(db.String(10), nullable=False)
    tipo_conta: Mapped[str] = mapped_column(db.String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, nullable=True, server_default='false')
    user_id: Mapped[int] = mapped_column(db.Integer, ForeignKey("public.user.id"), nullable=False)
    proposal_id: Mapped[int] = mapped_column(db.Integer, ForeignKey("public.proposal.id"), nullable=False)
    tipo_pagamento: Mapped[str] = mapped_column(db.String(50), nullable=False)
    bank: Mapped[int] = mapped_column(db.Integer, ForeignKey("public.bank.id"), nullable=False)

    def __repr__(self):
        return f"<ProposalWallet: {self.id}>"


class History(db.Model):
    __tablename__ = "history"
    __table_args__ = {'schema': 'public'}
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    proposal_id: Mapped[int] = mapped_column(db.Integer, ForeignKey("public.proposal.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(db.Integer, ForeignKey("public.user.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, server_default=func.now())
    action_at: Mapped[int] = mapped_column(db.Integer, nullable=True)
    action_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, nullable=True, server_default='false')
    description: Mapped[str] = mapped_column(db.String(255), nullable=False)
    
    def __repr__(self):
        return f"<History: {self.id}>"


class ManageOperation(db.Model):
    __tablename__ = "manage_operational"
    __table_args__ = {'schema': 'public'}
    
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    proposal_id: Mapped[int] = mapped_column(db.Integer, ForeignKey("public.proposal.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(db.Integer, ForeignKey("public.user.id"), nullable=False)
    number_proposal: Mapped[int] = mapped_column(db.Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f"<ManageOperation: {self.id}"

    
