from flask_sqlalchemy import pagination
from flask import (Blueprint, render_template, url_for, jsonify, abort, redirect, request, current_app, flash)
from flask_login import login_required, current_user 
from src import db


bp_operational = Blueprint("operational", __name__)


@bp_operational.route("/list-operational-contract")
@login_required
def manage_list_contract():
    
    return render_template("operational/manage_list.html")


@bp_operational.route("/manage-operational")
@login_required
def manage_operational():
    
    return render_template("operational/manage_operational.html")


@bp_operational.route("/state-contract")
@login_required
def manage_state_contract():
    
    return render_template("operational/state_contract.html")