from flask_login import UserMixin
from src import db 
from src.models.user import User


class Banker(db.Model, UserMixin):
    __tablename__ = 'bankers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    financial_agreements = db.relationship('FinancialAgreement', back_populates='banker')

class FinancialAgreement(db.Model, UserMixin):
    __tablename__ = 'financial_agreements'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    banker_id = db.Column(db.Integer, db.ForeignKey('bankers.id'))
    banker = db.relationship('Banker', back_populates='financial_agreements')
    tables_finance = db.relationship('TablesFinance', back_populates='financial_agreement', lazy='subquery')  # Mudado para subquery

class TablesFinance(db.Model, UserMixin):
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
    
class RankFlat(db.Model, UserMixin):
    __tablename__ = 'rank_flats'
    id = db.Column(db.Integer, primary_key=True)
    tables_finance_id = db.Column(db.Integer, db.ForeignKey('tables_finance.id'))
    tables_finance = db.relationship('TablesFinance', back_populates='rank_flats')

TablesFinance.rank_flats = db.relationship('RankFlat', back_populates='tables_finance')

# class ReportBanker(db, UserMixin):
#     """Conference report banker with tablesFynance"""
