import pandas as pd

from flask import Blueprint , render_template, request, redirect, url_for
from flask_login import login_required, current_user
from flask import jsonify
from src import db
from sqlalchemy.orm import joinedload
from src.models.bsmodels import Banker, FinancialAgreement, TablesFinance, ReportBankerTransactionData

bp_campaign = Blueprint("campaign", __name__)


@bp_campaign.route("/list-campaign")
@login_required
def manage_campaign():
    """
        Function manage campaing
    """
    
    return render_template("campaign/list_campaing.html")


@bp_campaign.route("add-campaign")
@login_required
def add_campaing():
    """
        Function campaing add 
    """

    return render_template("campaign/manage_campaing.html")