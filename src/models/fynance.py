from datetime import datetime
from flask_login import UserMixin
from src import db 
from src.models.user import User
from sqlalchemy.dialects.sqlite import JSON

class Banker(db.Model, UserMixin):
    """tabela do banco"""
    __tablename__ = 'bankers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    financial_agreements = db.relationship('FinancialAgreement', back_populates='banker')

class FinancialAgreement(db.Model, UserMixin):
    """Convenio do banco especifico"""
    __tablename__ = 'financial_agreements'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    banker_id = db.Column(db.Integer, db.ForeignKey('bankers.id'))
    banker = db.relationship('Banker', back_populates='financial_agreements')
    tables_finance = db.relationship('TablesFinance', back_populates='financial_agreement', lazy='subquery')  # Mudado para subquery

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
    banker_id = db.Column(db.Integer, db.ForeignKey('bankers.id'), nullable=False)
    conv_id = db.Column(db.Integer, db.ForeignKey('financial_agreements.id', ondelete='CASCADE'))
    financial_agreement = db.relationship('FinancialAgreement', back_populates='tables_finance')


class ReportBankerTransactionData(db.Model, UserMixin):
    """ 
    Keyword arguments: conection database init report banker 
    argument: post dynamic with report
    Return: get info database in report banker 
    """
    
    id = db.Column(db.Integer, primary_key=True)
    banker_id = db.Column(db.Integer, db.ForeignKey('bankers.id'))
    conv_id = db.Column(db.Integer, db.ForeignKey('financial_agreements.id'))
    data = db.Column(JSON, nullable=False)
    
    def __init__(self, banker_id, conv_id, data):
        self.banker_id = banker_id
        self.conv_id =  conv_id
        self.data =  data 

    
    



# class TableCartFinance(db.Model, UserMixin):
#     """Tabela cartão"""
#     __tablename__ = 'tables_finance_cart'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     type_table = db.Column(db.String(100), nullable=False)
#     table_code = db.Column(db.String(100), nullable=False)
#     rate = db.Column(db.String(100), nullable=False)
#     banker_id = db.Column(db.Integer, db.ForeignKey('bankers.id'), nullable=False)
#     conv_id = db.Column(db.Integer, db.ForeignKey('financial_agreements.id', ondelete='CASCADE'))
#     financial_agreement = db.relationship('FinancialAgreement', back_populates='tables_finance')

class RankFlat(db.Model, UserMixin):
    """"rank de tabela normal"""
    __tablename__ = 'rank_flats'
    id = db.Column(db.Integer, primary_key=True)
    tables_finance_id = db.Column(db.Integer, db.ForeignKey('tables_finance.id'))
    tables_finance = db.relationship('TablesFinance', back_populates='rank_flats')



# class DynamicData(db.Model, UserMixin):
#     __tablename__ = 'dynamic_data'
    
#     id = db.Column(db.Integer, primary_key=True)
#     banco = db.Column(db.String(255), nullable=False)
#     convenio = db.Column(db.String(255), nullable=False)
#     column_name = db.Column(db.String(255), nullable=False)  # Nome da coluna
#     value = db.Column(db.String(255), nullable=False)        # Valor da coluna

#     def __init__(self, banco, convenio, column_name, value):
#         self.banco = banco
#         self.convenio = convenio
#         self.column_name = column_name
#         self.value = value



# class RankFlatCart(db.Model, UserMixin):
#     """rank de tabela de cartão"""
#     __tablename__ = 'ranks_flats_cart'
#     id = db.Column(db.Integer, primary_key=True)
#     tables_finance_id = db.Column(db.Integer, db.ForeignKey('tables_finance_cart.id'))
#     tables_finance = db.relationship('tables_finance_cart', back_populates='ranks_flats_cart')
    
    
# class CompaingComission(db.Model, UserMixin):
#     """Campanha de comissão sendo excluida algum"""
#     __tablename__ = 'comission'
#     id = db.Column(db.Integer, primary_key=True)
#     table = db.Column(db.String(100), nullable=False)
#     value = db.Column(db.Float, nullable=False)
#     active = db.Column(db.Boolean, default=True)
#     creat_at = db.Column(db.DateTime, default=datetime.utcnow)
#     usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
#     user = db.relationship('user', backref='comissoes')


# class ReportComissionBanker(db.Model, UserMixin):
#     __tablename__ = 'report_banker' # relatorio do banco
#     id = db.Column(db.Integer, primary_key=True)
    
    


TablesFinance.rank_flats = db.relationship('RankFlat', back_populates='tables_finance')

# class ReportBanker(db, UserMixin):
#     """Conference report banker with tablesFynance"""
