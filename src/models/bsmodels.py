from flask_login import UserMixin
from src import db
from sqlalchemy.dialects.sqlite import JSON
from datetime import datetime
from werkzeug.security import generate_password_hash
from sqlalchemy import func

class Banker(db.Model, UserMixin):
    """Tabela do banco"""
    __tablename__ = 'bankers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    financial_agreements = db.relationship('FinancialAgreement', back_populates='banker')
    comissions = db.relationship('CalcComissionRate', back_populates='banker')

class FinancialAgreement(db.Model, UserMixin):
    """Convenio do banco especifico"""
    __tablename__ = 'financial_agreements'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    banker_id = db.Column(db.Integer, db.ForeignKey('bankers.id'))
    banker = db.relationship('Banker', back_populates='financial_agreements')
    tables_finance = db.relationship('TablesFinance', back_populates='financial_agreement', lazy='subquery')


class TablesFinance(db.Model, UserMixin):
    """Tabela normal"""
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


class ReportBankerTransactionData(db.Model, UserMixin):
    """Report de transações do banco"""
    __tablename__ = 'report_banker_transaction_data'
    id = db.Column(db.Integer, primary_key=True)
    banker_id = db.Column(db.Integer, db.ForeignKey('bankers.id'))
    conv_id = db.Column(db.Integer, db.ForeignKey('financial_agreements.id'))
    data = db.Column(JSON, nullable=False)

    def __init__(self, banker_id, conv_id, data):
        self.banker_id = banker_id
        self.conv_id = conv_id
        self.data = data


class RankFlat(db.Model, UserMixin):
    """Rank de tabela normal"""
    __tablename__ = 'rank_flats'
    id = db.Column(db.Integer, primary_key=True)
    tables_finance_id = db.Column(db.Integer, db.ForeignKey('tables_finance.id'))
    tables_finance = db.relationship('TablesFinance', back_populates='rank_flats')


class CalcComissionRate(db.Model, UserMixin):
    """
    Tabela para armazenar o cálculo do repasse de comissão das tabelas por usuários.
    """
    __tablename__ = 'calc_comission'
    id = db.Column(db.Integer, primary_key=True)
    banker_id = db.Column(db.Integer, db.ForeignKey('bankers.id'), nullable=False)
    table_finance_id = db.Column(db.Integer, db.ForeignKey('tables_finance.id'), nullable=False)
    proposal_id = db.Column(db.Integer, db.ForeignKey('proposal.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    valor_comissao = db.Column(db.Float, nullable=False)
    repasse_comissao = db.Column(db.Float, nullable=False)
    percentage_applied = db.Column(db.Float, nullable=False)

    banker = db.relationship('Banker', back_populates='comissions')
    tables_finance = db.relationship('TablesFinance', back_populates='comissions')
    proposal = db.relationship('UserProposal', back_populates='comissions')
    user = db.relationship('User', back_populates='comissions')
    proposal = db.relationship('UserProposal', back_populates='comissions')


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
    comissions = db.relationship('CalcComissionRate', back_populates='user')

    # Relationship
    points = db.relationship('Point', back_populates='user', lazy='dynamic')
    vacations = db.relationship('VocationBs', back_populates='user', lazy='dynamic')
    permissions = db.relationship('UserPermission', backref='user', lazy='dynamic')

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


class Permission(db.Model):
    __tablename__ = 'permissions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    users = db.relationship('UserPermission', backref='permission', lazy='dynamic')

    def __repr__(self):
        return f"<Permission {self.name}>"


class UserPermission(db.Model):
    __tablename__ = 'user_permissions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<UserPermission {self.user_id} - {self.permission_id}>"
    
class UserProposal(db.Model, UserMixin):
    __tablename__ = 'proposal'
    
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_creator_id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
    banker_id = db.Column(db.Integer, db.ForeignKey('bankers.id', name='fk_banker_id'), nullable=False)
    conv_id = db.Column(db.Integer, db.ForeignKey('financial_agreements.id', name='fk_conv_id'), nullable=False)
    table_id = db.Column(db.Integer, db.ForeignKey('tables_finance.id', name='fk_table_id'), nullable=False)
    operation_select = db.Column(db.String(40), nullable=False)
    matricula = db.Column(db.String(100), nullable=False)
    text_password_server = db.Column(db.String(100))
    ddb = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
    passowrd_chek = db.Column(db.String(50), nullable=False)
    name_and_lastname = db.Column(db.String(100), nullable=False)
    dd_year = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
    sex = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    cpf = db.Column(db.String(30), nullable=False)
    naturalidade = db.Column(db.String(30), nullable=False)
    select_state = db.Column(db.String(10), nullable=False)
    identify = db.Column(db.String(30), nullable=False)
    organ_emissor = db.Column(db.String(30), nullable=False)
    uf_emissor = db.Column(db.String(10), nullable=False)
    day_emissor = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
    name_father = db.Column(db.String(30), nullable=False)
    name_mother = db.Column(db.String(30), nullable=False)
    zipcode = db.Column(db.String(30), nullable=False)
    address = db.Column(db.String(30), nullable=False)
    address_number = db.Column(db.String(30), nullable=False)
    address_complement = db.Column(db.String(20))
    neighborhood = db.Column(db.String(30), nullable=False)
    city = db.Column(db.String(30), nullable=False)
    state_uf_city = db.Column(db.String(10), nullable=False)
    value_salary = db.Column(db.String(30), nullable=False)
    value_salaray_liquid = db.Column(db.String(30), nullable=False)
    phone = db.Column(db.String(30))
    phone_residential = db.Column(db.String(30))
    phone_comercial = db.Column(db.String(30))
    benefit_select = db.Column(db.String(100))
    uf_benefit_select = db.Column(db.String(10), nullable=False)
    select_banker_payment_type = db.Column(db.String(30), nullable=False)
    select_banker_payment = db.Column(db.String(20), nullable=False)
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
    margem = db.Column(db.String(30), nullable=False)
    parcela = db.Column(db.String(30), nullable=False)
    prazo = db.Column(db.String(30), nullable=False)
    value_operation = db.Column(db.String(30), nullable=False)
    obeserve = db.Column(db.String(500), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=False) # status proposal 
    block = db.Column(db.Boolean, nullable=False, default=False) #  status block for active
    is_status = db.Column(db.Boolean, nullable=True, default=False)
     
    # Relationship
    creator = db.relationship('User', backref='created_proposals', foreign_keys=[creator_id])
    banker = db.relationship('Banker', foreign_keys=[banker_id])
    financial_agreement = db.relationship('FinancialAgreement', foreign_keys=[conv_id])
    comissions = db.relationship('CalcComissionRate', back_populates='proposal')  # Certifique-se de que o nome esteja correto


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