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
    comissions = db.relationship('CalcComissionRate', back_populates='banker')
    
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
    
    def __init__(self, name):
        self.name = name


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
    conv_id = db.Column(db.Integer, db.ForeignKey('financial_agreements.id', ondelete='CASCADE'))
    financial_agreement = db.relationship('FinancialAgreement', back_populates='tables_finance')
    comissions = db.relationship('CalcComissionRate', back_populates='tables_finance')
    rank_flats = db.relationship('RankFlat', back_populates='tables_finance')
    
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

class ReportBankerTransactionData(db.Model, UserMixin):
    """
        Salvando o template de relatorio de comissão pagas do banco
    """
    __tablename__ = 'report_banker_transaction_data'
    id = db.Column(db.Integer, primary_key=True)
    banker_id = db.Column(db.Integer, db.ForeignKey('bankers.id'))
    data = db.Column(JSON, nullable=False)
    
    def __init__(self, banker_id, data):
        self.banker_id = banker_id
        self.data = data

class RankFlat(db.Model, UserMixin):
    """
        Rank de Flats
    """
    __tablename__ = 'rank_flats'
    id = db.Column(db.Integer, primary_key=True)
    tables_finance_id = db.Column(db.Integer, db.ForeignKey('tables_finance.id'))
    tables_finance = db.relationship('TablesFinance', back_populates='rank_flats')

class CalcComissionRate(db.Model):
    __tablename__ = 'calc_comission'
    
    id = db.Column(db.Integer, primary_key=True)
    banker_id = db.Column(db.Integer, db.ForeignKey('bankers.id'), nullable=False)
    table_finance_id = db.Column(db.Integer, db.ForeignKey('tables_finance.id'), nullable=False)
    proposal_id = db.Column(db.Integer, db.ForeignKey('proposal.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)

    value_comission = db.Column(db.Float, nullable=False)
    next_comission = db.Column(db.Float, nullable=False)
    percentage_applied = db.Column(db.Float, nullable=False)
    comission_apply = db.Column(db.Boolean, default=False)
    day_payment = db.Column(db.DateTime)

    # Relationships
    banker = db.relationship('Banker', back_populates='comissions')
    tables_finance = db.relationship('TablesFinance', back_populates='comissions')
    proposal = db.relationship('Proposal', back_populates='comissions')
    user = db.relationship('User', back_populates='comissions')
    room = db.relationship('Roomns', back_populates='comissions')

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
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_block = db.Column(db.Boolean, nullable=False, default=False)
    is_inactive = db.Column(db.Boolean, nullable=False, default=False)
    is_comission = db.Column(db.Boolean, nullable=False, default=False)
    created_on = db.Column(db.DateTime, nullable=False, default=func.now())
    
    # Relationships
    comissions = db.relationship('CalcComissionRate', back_populates='user')
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
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
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
    value_operation = db.Column(db.String(30))
    obeserve = db.Column(db.String(500))
    active = db.Column(db.Boolean, nullable=False, default=False)
    block = db.Column(db.Boolean, nullable=False, default=False)
    is_status = db.Column(db.Boolean, nullable=True, default=False)
    progress_check = db.Column(db.Boolean, nullable=True, default=False)
    edit_at = db.Column(db.DateTime(timezone=True), nullable=True)
    completed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    number_proposal = db.Column(db.String(30), nullable=True, default=None)

    # Relationships
    creator = db.relationship('User', back_populates='created_proposals', foreign_keys=[creator_id])
    banker = db.relationship('Banker', foreign_keys=[banker_id])
    financial_agreement = db.relationship('FinancialAgreement', foreign_keys=[conv_id])
    comissions = db.relationship('CalcComissionRate', back_populates='proposal')

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
    comissions = db.relationship('CalcComissionRate', back_populates='room')
