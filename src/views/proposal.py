from flask import Blueprint, render_template
from flask import url_for, jsonify, abort
from flask import redirect, request
from flask_login import login_required
from src import db 
from ..models.proposal import UserProposal, UserProposalOperationData, UserProposalBanker
from ..models.fynance import Banker, FinancialAgreement


bp_proposal = Blueprint("proposal", __name__)


@bp_proposal.route("/proposal")
@login_required
def get_proposal():
    bankers = Banker.query.options(
        db.joinedload(Banker.financial_agreements).subqueryload(FinancialAgreement.tables_finance)
    ).order_by(Banker.name).all()
    return render_template("proposal/gerement_proposal.html", banks=bankers)


@bp_proposal.route("/proposal/status")
def get_status_proposal():
    return render_template("proposal/status_proposal.html")