from sqlalchemy import func
from flask_login import UserMixin
from src import db 
from src.models.user import User
from datetime import datetime

class UserProposal(db.Model, UserMixin):
    __tablename__ = 'proposal'
    
    id = db.Column(db.Integer, primary_key=True) # id
    created_at = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String, nullable=False) # nome
    cpf = db.Column(db.String, nullable=False) # cpf
    lastname = db.Column(db.String(150), unique=False, nullable=False) # sobrenome 
    email= db.Column(db.String(150), nullable=False) # email 
    date_created = db.Column(db.DateTime(timezone=True), default=func.now()) # data de criação 
    date_year = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False) #  data de nascimento
    sex_user = db.Column(db.String(20), nullable=False) # sexo do usuário 
    password_against_check = db.Column(db.String(100), nullable=False) # senha do contra-cheque
    naturalness = db.Column(db.String(100), nullable=False) # naturalidade 
    naturalness_uf = db.Column(db.String(100), nullable=False) # uf da naturalidade 
    identity = db.Column(db.String(100), nullable=False) #  identidade 
    organ_sender_identity = db.Column(db.String(100), nullable=False) # orgão emissor da identidade 
    uf_sender_identity = db.Column(db.String(100), nullable=False) #  uf do orgãoo emissor da identidade
    day_uf_sender_identity = db.Column(db.DateTime(timezone=True), nullable=False) # data da emissão da identidade 
    name_father = db.Column(db.String(100), nullable=False) # nome do pai
    name_mother = db.Column(db.String(100), nullable=False) # nome da mãe
    zip_code = db.Column(db.String(100), nullable=False) # cep
    address = db.Column(db.String(100), nullable=False) # endereço
    number = db.Column(db.String(100), nullable=False)  # número do endereço
    complement_address = db.Column(db.String(100), default=None) # complemento 
    neighborhood = db.Column(db.String(100), nullable=False) # bairro 
    city = db.Column(db.String(100), nullable=False) # city
    uf = db.Column(db.String(12), nullable=False) # uf city
    value_wage = db.Column(db.String(100), nullable=False)
    phone_house = db.Column(db.String(100)) # telefone residencial
    phone_commercial = db.Column(db.String(100)) # telefone cormercial 
    phone_user = db.Column(db.String(100)) # telefone pessoal 
    benefit_user = db.Column(db.String(100)) # especie de beneficio 
    uf_benefit_user = db.Column(db.String(12)) # uf da especie do beneficio 
    
    def __init__(self, created_at, name, cpf, lastname, email, sex_user, password_against_check, naturalness, naturalness_uf, identity, organ_sender_identity, 
                 uf_sender_identity, day_uf_sender_identity, name_father, name_mother, zip_code, address, number, neighborhood, city, uf, 
                 value_wage, phone_house=None, phone_commercial=None, phone_user=None, benefit_user=None, uf_benefit_user=None, 
                 complement_address=None):
        self.created_at = created_at
        self.name = name
        self.cpf = cpf
        self.lastname = lastname
        self.email = email
        self.date_created = datetime.now()
        self.date_year = datetime.now()
        self.sex_user = sex_user
        self.password_against_check = password_against_check
        self.naturalness = naturalness
        self.naturalness_uf = naturalness_uf
        self.identity = identity
        self.organ_sender_identity = organ_sender_identity
        self.uf_sender_identity = uf_sender_identity
        self.day_uf_sender_identity = day_uf_sender_identity
        self.name_father = name_father
        self.name_mother = name_mother
        self.zip_code = zip_code
        self.address = address
        self.number = number
        self.neighborhood = neighborhood
        self.city = city
        self.uf = uf
        self.value_wage = value_wage
        self.phone_house = phone_house
        self.phone_commercial = phone_commercial
        self.phone_user = phone_user
        self.benefit_user = benefit_user
        self.uf_benefit_user = uf_benefit_user
        self.complement_address = complement_address
        
    def __repr__(self):
        return f"<{id} in proposal>"
    

class UserProposalBanker(db.Model, UserMixin):
    
    __tablename__ = 'databanker'
    id = db.Column(db.Integer, primary_key=True) # id
    proposalid = db.Column(db.Integer, db.ForeignKey('proposal.id'), nullable=False) # correlação com o id da proposta
    type_pagament = db.Column(db.String(20), nullable=False) # tipo do pagamento
    banker = db.Column(db.String(100), nullable=False) # banco 
    question_benefit_cart = db.Column(db.String(10), nullable=False)
    agency = db.Column(db.String(100), nullable=False) # agencia
    agency_dv  = db.Column(db.String(100), nullable=False) # banco 
    account_banker = db.Column(db.String(100), nullable=False) # conta do banco 
    type_banker = db.Column(db.String(20), nullable=False)  # tipo da conta 
    
    def __init__(self, proposalid, type_pagament, banker, question_benefit_cart, agency, agency_dv, account_banker, type_banker):
        self.proposalid = proposalid
        self.type_pagament = type_pagament
        self.banker = banker
        self.question_benefit_cart = question_benefit_cart
        self.agency = agency
        self.agency_dv = agency_dv
        self.account_banker = account_banker
        self.type_banker = type_banker
    
    
    
class UserProposalOperationData(db.Model, UserMixin):
    __tablename__ = 'opeationdata'
    id = db.Column(db.Integer, primary_key=True) # id
    proposalid = db.Column(db.Integer, db.ForeignKey('proposal.id'), nullable=False) # correlação com o id da proposta
    userproposalbankerid = db.Column(db.Integer, db.ForeignKey('proposal.id'), nullable=False) # correlação com o id dos dados bancarios
    free_margin = db.Column(db.String(100), nullable=False)
    tariff = db.Column(db.String(100))
    portion = db.Column(db.String(100)) 
    term = db.Column(db.String(100)) 
    coefficient = db.Column(db.String(100)) 
    tac = db.Column(db.String(100))
    value = db.Column(db.String(100))
    value_client = db.Column(db.String(100))
    observe = db.Column(db.String(400))
    
    def __init__(self, proposalid, userproposalbankerid, free_margin, tariff=None, portion=None, term=None, coefficient=None, tac=None, value=None, value_client=None, observe=None):
        self.proposalid = proposalid
        self.userproposalbankerid = userproposalbankerid
        self.free_margin = free_margin
        self.tariff = tariff
        self.portion = portion
        self.term = term
        self.coefficient = coefficient
        self.tac = tac
        self.value = value
        self.value_client = value_client
        self.observe = observe