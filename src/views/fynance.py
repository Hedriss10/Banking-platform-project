import pandas as pd

from flask import Blueprint , render_template, request, redirect, url_for
from flask_login import login_required
from flask import jsonify
from flask_login import current_user
from flask_login import login_required
from src import db
from sqlalchemy.orm import joinedload
from ..models.fynance import Banker, FinancialAgreement, TablesFinance
from werkzeug.utils import secure_filename


bp_fynance = Blueprint("fynance", __name__)


@bp_fynance.route("/bankers")
@login_required
def get_register_bankers():
    """Get modal operation bankers""" 
    return render_template("fynance/register_bankers.html")


@bp_fynance.route("/get-bankers")
@login_required
def get_list_bankers():
    """Get list all bankers"""
    bankers = Banker.query.options(
        db.joinedload(Banker.financial_agreements).subqueryload(FinancialAgreement.tables_finance)
    ).order_by(Banker.name).all()
    return render_template("fynance/list_bankers.html", banks=bankers)

@bp_fynance.route("/get-register-coven")
@login_required
def get_register_conven():
    """Register coven, return banker for register conv in banker"""
    bankers = Banker.query.order_by(Banker.name).all()
    return render_template("fynance/register_conven.html", banks=bankers)


@bp_fynance.route("/get-report-banker")
@login_required
def get_register_report():
    """Report banker with report system"""
    bankers = Banker.query.options(joinedload(Banker.financial_agreements)).order_by(Banker.name).all()
    return render_template("fynance/report_bankers.html", banks=bankers)


@bp_fynance.route("/register-convenio", methods=['POST'])
@login_required
def post_register_conven():
    """Register conven bankers"""
    data = request.json
    conv_name = data.get('name')
    bank_id = data.get('bank_id')

    if not conv_name:
        return jsonify({"error": 'Conven name is required'}), 400
    if not bank_id:
        return jsonify({"error": 'Bank ID is required'}), 400
    try:
        bank_id = int(bank_id)
    except ValueError:
        return jsonify({"error": "Bank ID must be an integer"}), 400
    
    try:
        name_conv = FinancialAgreement(name=conv_name, banker_id=bank_id)
        db.session.add(name_conv)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bp_fynance.route("/register-bankers", methods=['POST'])
@login_required
def post_register_bankers():
    """Register bankers unique violation"""
    data = request.json
    bank_name = data.get('name')
    if not bank_name:
        return jsonify({'error': 'Bank name is required'}), 400

    existing_bank = Banker.query.filter_by(name=bank_name).first()
    if existing_bank:
        return jsonify({'error': 'Esse banco já existe!'}), 409

    try:
        new_banker = Banker(name=bank_name)
        db.session.add(new_banker)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp_fynance.route("/register-bankers/tables", methods=['POST'])
@login_required
def register_tables_bankers():
    """rout api for import tables in large quantities"""
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    bank_id = request.form['bankSelect']
    convenio_id = request.form['convenioSelect']
    
    if not file:
        return jsonify({'error': 'No file provided'}), 400

    filename = secure_filename(file.filename)
    if filename.endswith(('.csv', '.xlsx', ';', ',')):
        if filename.endswith('.csv') or filename.endswith(','):
            data = pd.read_csv(file, dtype="object", sep=",")
        elif filename.endswith(';'):
            data = pd.read_csv(file, dtype="object", sep=";")
        elif filename.endswith('.xlsx'):
            data = pd.read_excel(file, dtype="object")
        else: jsonify({"error": 'Invalid type formart'}), 400
    else:
        return jsonify({'error': 'Invalid file format'}), 400
    
    try:
        for index, row in data.iterrows():
            new_table = TablesFinance(
                name=row['Tabela'], 
                table_code=row['Cod Tabela'],
                type_table=row['Tipo'],
                start_term=row['Prazo Inicio'],
                end_term=row['Prazo Fim'],
                rate=row['Flat'],
                banker_id=bank_id,
                conv_id=convenio_id,
            )
            db.session.add(new_table)
        db.session.commit()
        return redirect(url_for("overview.home"))
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp_fynance.route("/register-bankers/tables/banker/conv/one", methods=['POST'])
@login_required
def register_tables_one():
    """Endpoint for registering one table for bank and conv select"""
    bank_id = request.form['bankSelectOne']
    convenio_id = request.form['convenioSelect']
    name = request.form['name']
    type_table = request.form['type_table']
    table_code = request.form['tablecode']
    start_term = request.form['start_term']
    end_term = request.form['end_term']
    rate = request.form['rate']
    
    try:
        new_table = TablesFinance(
            name=name, 
            table_code=table_code,
            type_table=type_table,
            start_term=start_term,
            end_term=end_term,
            rate=rate,
            banker_id=bank_id,
            conv_id=convenio_id,
        )
        db.session.add(new_table)
        db.session.commit()
        return redirect(url_for("overview.home"))
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    

@bp_fynance.route("/delete-bankers/<int:id>", methods=['POST'])
@login_required
def delete_bankers(id):
    banker = Banker.query.get_or_404(id)
    db.session.delete(banker)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Banco deletado com sucesso!'}), 200
    

@bp_fynance.route("/delete-bankers/conv/<int:id>", methods=['POST'])
@login_required
def delete_conv_in_banker(id):
    convenio = FinancialAgreement.query.get_or_404(id)
    db.session.delete(convenio)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Convênio deletado com sucesso!'}), 200


@bp_fynance.route("/delete-bankers/conv/tables/<int:id>", methods=['POST'])
@login_required
def delete_table_in_conv_in_banker(id):
    table = TablesFinance.query.get_or_404(id)
    db.session.delete(table)
    db.session.commit()
    return jsonify({"success": True, 'message': 'Tabela deletada com sucesso!'}), 200

