from sqlalchemy import func
from flask_login import UserMixin
from src import db 
from src.models.user import User



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


class StateProposal(db.Model, UserMixin):
    __tablename__ = 'state_proposal'
    
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_creator_id'), nullable=False)
    proposal_id = db.Column(db.Integer, db.ForeignKey('proposal.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=func.now(), nullable=False)
    obeserve = db.Column(db.String(500), nullable=False)
    
    # Relationship
    proposal = db.relationship('UserProposal', backref=db.backref('statuses', lazy='dynamic'))
