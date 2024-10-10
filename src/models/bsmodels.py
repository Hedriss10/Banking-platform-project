from flask_login import UserMixin
from src import db
from sqlalchemy.dialects.sqlite import JSON
from datetime import datetime
from werkzeug.security import generate_password_hash
from sqlalchemy import func


class Banker(db.Model, UserMixin):
    """
        Tabela do banco
    """
    __tablename__ = 'bankers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    financial_agreements = db.relationship('FinancialAgreement', back_populates='banker')
    
    def __init__(self, name):
        self.name = name


class FinancialAgreement(db.Model, UserMixin):
    """
        Cadastro de um convenio em um banco especifico
    """
    __tablename__ = 'financial_agreements'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    banker_id = db.Column(db.Integer, db.ForeignKey('bankers.id'))
    banker = db.relationship('Banker', back_populates='financial_agreements')
    tables_finance = db.relationship('TablesFinance', back_populates='financial_agreement', lazy='subquery')
    
    def __init__(self, name, banker_id):
        self.name = name
        self.banker_id = banker_id


class TablesFinance(db.Model, UserMixin):
    """
        Cadastrando as tabelas bancarias no sistema
    """
    __tablename__ = 'tables_finance'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type_table = db.Column(db.String(100), nullable=False)
    table_code = db.Column(db.String(100), nullable=False)
    start_term = db.Column(db.String(100), nullable=False)
    end_term = db.Column(db.String(100), nullable=False)
    rate = db.Column(db.String(100), nullable=False)
    is_status = db.Column(db.Boolean, nullable=True, default=None)
    banker_id = db.Column(db.Integer, db.ForeignKey('bankers.id'), nullable=False)
    conv_id = db.Column(db.Integer, db.ForeignKey('financial_agreements.id'))
    financial_agreement = db.relationship('FinancialAgreement', back_populates='tables_finance')
    rank_flats = db.relationship('RankFlat', back_populates='tables_finance')
    commission = db.Column(db.Float, nullable=True, default=None)

    
    def __init__(self, name, type_table, table_code, start_term, end_term, rate, is_status, banker_id, conv_id):
        self.name = name
        self.type_table = type_table
        self.table_code = table_code
        self.start_term = start_term
        self.end_term = end_term
        self.rate = rate
        self.is_status = is_status
        self.banker_id = banker_id
        self.conv_id = conv_id

    def __repr__(self) -> str:
        return f"Tables register successful {self.name}"


class RankFlat(db.Model, UserMixin):
    """
        Rank de Flats
    """
    __tablename__ = 'rank_flats'
    id = db.Column(db.Integer, primary_key=True)
    tables_finance_id = db.Column(db.Integer, db.ForeignKey('tables_finance.id'))
    tables_finance = db.relationship('TablesFinance', back_populates='rank_flats')


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    user_identification = db.Column(db.String(100))
    username = db.Column(db.String(150), nullable=False)
    lastname = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150))
    type_user_func = db.Column(db.String(100), nullable=False)
    typecontract = db.Column(db.String(30), nullable=False)
    session_token = db.Column(db.String(150), nullable=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_block = db.Column(db.Boolean, nullable=False, default=False)
    is_inactive = db.Column(db.Boolean, nullable=False, default=False)
    is_comission = db.Column(db.Boolean, nullable=False, default=False)
    created_on = db.Column(db.DateTime, nullable=False, default=func.now())
    
    # Relationships
    created_rooms = db.relationship('Roomns', back_populates='creator')
    created_proposals = db.relationship('Proposal', back_populates='creator')
    # 'rooms' relationship is available via backref from Roomns.users
    
    def __init__(self, user_identification, username, lastname, email, type_user_func, typecontract, password, is_admin=False, is_block=False, is_inactive=False, is_comission=False):
        self.user_identification = user_identification
        self.username = username
        self.lastname = lastname
        self.email = email
        self.type_user_func = type_user_func
        self.typecontract = typecontract
        self.password = generate_password_hash(password)
        self.is_admin = is_admin
        self.is_block = is_block
        self.is_inactive = is_inactive
        self.is_comission = is_comission

    def __repr__(self):
        return f"<ID {self.user_identification}>"


class Proposal(db.Model, UserMixin):
    """
        User Proposal
    """
    __tablename__ = 'proposal'
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_creator_id'))
    created_at = db.Column(db.DateTime(timezone=True))
    banker_id = db.Column(db.Integer, db.ForeignKey('bankers.id', name='fk_banker_id'))
    conv_id = db.Column(db.Integer, db.ForeignKey('financial_agreements.id', name='fk_conv_id'))
    table_id = db.Column(db.Integer, db.ForeignKey('tables_finance.id', name='fk_table_id'))
    operation_select = db.Column(db.String(40))
    matricula = db.Column(db.String(100))
    passowrd_chek = db.Column(db.String(50))
    name = db.Column(db.String(50))
    lastname = db.Column(db.String(50))
    date_year = db.Column(db.DateTime(timezone=True), default=func.now())
    sex = db.Column(db.String(30))
    email = db.Column(db.String(30))
    cpf = db.Column(db.String(30))
    naturalidade = db.Column(db.String(30))
    select_state = db.Column(db.String(10))
    identify_document = db.Column(db.String(30))
    organ_emissor = db.Column(db.String(30))
    uf_emissor = db.Column(db.String(10))
    day_emissor = db.Column(db.DateTime(timezone=True), default=func.now())
    name_father = db.Column(db.String(30))
    name_mother = db.Column(db.String(30))
    zipcode = db.Column(db.String(30))
    address = db.Column(db.String(30))
    address_number = db.Column(db.String(30))
    address_complement = db.Column(db.String(20))
    neighborhood = db.Column(db.String(30))
    city = db.Column(db.String(30))
    state_uf_city = db.Column(db.String(10), nullable=False)
    value_salary = db.Column(db.String(30), nullable=False)
    value_salaray_liquid = db.Column(db.String(30), nullable=False)
    phone = db.Column(db.String(30))
    phone_residential = db.Column(db.String(30))
    phone_comercial = db.Column(db.String(30))
    benefit_select = db.Column(db.String(100))
    uf_benefit_select = db.Column(db.String(10))
    select_banker_payment_type = db.Column(db.String(30))
    select_banker_payment = db.Column(db.String(20))
    receivedcardbenefit = db.Column(db.String(10))
    agency_bank = db.Column(db.String(30))
    pix_type_key = db.Column(db.String(10))
    agency = db.Column(db.String(10))
    agency_dv = db.Column(db.String(10))
    account = db.Column(db.String(10))
    account_dv = db.Column(db.String(10))
    type_account = db.Column(db.String(10))
    agency_op = db.Column(db.String(10))
    agency_dvop = db.Column(db.String(10))
    margem = db.Column(db.String(30))
    parcela = db.Column(db.String(30))
    prazo = db.Column(db.String(30))
    value_operation = db.Column(db.Numeric(precision=10, scale=3), nullable=True, default=0.0)
    obeserve = db.Column(db.String(500))
    
    # status contrac
    aguardando_digitacao = db.Column(db.Boolean, nullable=True, default=False)
    pendente_digitacao = db.Column(db.Boolean, nullable=True, default=False)
    contrato_digitacao = db.Column(db.Boolean, nullable=True, default=False) 
    aguardando_aceite_do_cliente = db.Column(db.Boolean, nullable=True, default=False) 
    aceite_feito_analise_do_banco = db.Column(db.Boolean, nullable=True, default=False) 
    contrato_pendente_pelo_banco = db.Column(db.Boolean, nullable=True, default=False)
    aguardando_pagamento = db.Column(db.Boolean, nullable=True, default=False)
    contratopago = db.Column(db.Boolean, nullable=True, default=False)
    
    edit_at = db.Column(db.DateTime(timezone=True), nullable=True)
    completed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    number_proposal = db.Column(db.String(30), nullable=True, default=None)
    completed_by = db.Column(db.String(10), nullable=True, default=None)
    deleted_at = db.Column(db.String(10), nullable=True, default=None)
    is_status = db.Column(db.Boolean, nullable=True, default=None)

    # Relationships
    creator = db.relationship('User', back_populates='created_proposals', foreign_keys=[creator_id])
    banker = db.relationship('Banker', foreign_keys=[banker_id])
    financial_agreement = db.relationship('FinancialAgreement', foreign_keys=[conv_id])
    table_finance = db.relationship('TablesFinance', backref='proposals')


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
    creator = db.relationship('User', back_populates='created_rooms')
    users = db.relationship('User', secondary=room_user_association, backref='rooms')


class ReportData(db.Model):
    __tablename__ = 'report_data'

    id = db.Column(db.Integer, primary_key=True)
    report_name = db.Column(db.String(100), nullable=False)  # Nome do relatório
    date_import = db.Column(db.DateTime) # data da importação
    cpf = db.Column(db.String(14), nullable=False)  # CPF do registro
    number_proposal = db.Column(db.String(30), nullable=False)  # Número da proposta
    table_code = db.Column(db.String(30), nullable=False)  # Código da tabela
    is_valid = db.Column(db.Boolean, nullable=False, default=False)  # Se o registro foi validado
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Relacionado ao usuário que importou


class Wallet(db.Model):
    
    __tablename__ = 'wallet'
    
    id = db.Column(db.Integer, primary_key=True)
    proposal_number = db.Column(db.String(100), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    value_operation = db.Column(db.Float, nullable=False)
    commission_rate = db.Column(db.Float, nullable=False)
    taxe_comission_rate = db.Column(db.Float, nullable=False, default=0.0)
    valor_base = db.Column(db.Float, nullable=False)
    repasse_comissao = db.Column(db.Float, nullable=False)
    date_created = db.Column(db.DateTime)
    cpf = db.Column(db.String(30), nullable=True)
    table_code = db.Column(db.String(20))

    seller = db.relationship('User', backref='wallet_entries')
