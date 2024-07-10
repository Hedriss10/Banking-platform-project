from flask import Blueprint, render_template
from flask import url_for, jsonify, abort
from flask import redirect, request
from flask_login import login_required
from sqlalchemy.orm import joinedload
from src import db 
from ..models.proposal import UserProposal, UserProposalOperationData, UserProposalBanker
from ..models.fynance import Banker, FinancialAgreement, TablesFinance


bp_proposal = Blueprint("proposal", __name__)


@bp_proposal.route("/proposal")
@login_required
def get_proposal():
    bankers = Banker.query.options(
        joinedload(Banker.financial_agreements).joinedload(FinancialAgreement.tables_finance)
    ).order_by(Banker.name).all()
    return render_template("proposal/gerement_proposal.html", bankers=bankers)


@bp_proposal.route("/proposal/status")
def get_status_proposal():
    return render_template("proposal/status_proposal.html")


@bp_proposal.route("/proposal/new-proposal", methods=['POST'])
def add_proposal():
    data = request.json 
    try:
        data = request.json 
        print(data)
        return jsonify({'message': 'Dados recebidos com sucesso'}), 200
    
    except Exception as e:
        print(f"{e}")
        
