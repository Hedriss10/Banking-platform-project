import pandas as pd
import io

from flask import Blueprint , render_template, request, redirect, url_for, make_response
from flask_login import login_required, current_user
from flask import jsonify
from src import db
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename
from src.models.bsmodels import Banker, FinancialAgreement, TablesFinance,  Proposal, User, Roomns, ReportData
from src.utils.fynance import calculate_commission

from datetime import datetime

bp_fynance = Blueprint("fynance", __name__)


@bp_fynance.route("/gerement-fynance")
@login_required
def gerement_finance():
    """manager banker 
        Registration of tables, management of banks, and agreements, 
        the bank and the agreement are in dynamic mode, where you create either one, 
        it will be presented according to the action and database search.
    Returns:
        _type_: _manager banker_
    """
    
    bankers = Banker.query.options(
        db.joinedload(Banker.financial_agreements).subqueryload(FinancialAgreement.tables_finance)
    ).order_by(Banker.name).all()
    for banker in bankers:
        for agreement in banker.financial_agreements:
            agreement.tables_finance = [
                table for table in agreement.tables_finance if table.is_status == 0
            ]
    return render_template("fynance/manager_banker.html", banks=bankers)


@bp_fynance.route("/manage-comission")
@login_required
def manage_comission():
    """_summary_
        rank de comissão de acordo com a maiores tabelas
    Returns:
        _type_: _rank_comission
    """
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search_term = request.args.get('search', '').lower()
    
    query = TablesFinance.query.join(FinancialAgreement).join(Banker)
    
    try:
        search_rate = float(search_term)
    except ValueError:
        search_rate = None

    if search_term:
        query = query.filter(
            TablesFinance.name.ilike(f'%{search_term}%') |   # Filtro pelo nome da tabela
            TablesFinance.table_code.ilike(f'%{search_term}%') |  # Filtro pelo código da tabela
            Banker.name.ilike(f'%{search_term}%') |   # Filtro pelo nome do banco
            FinancialAgreement.name.ilike(f'%{search_term}%') |  # Filtro pelo nome do convênio
            (TablesFinance.rate == search_rate if search_rate is not None else False)  # Filtro pela taxa de comissão
        )

    tables_paginated = query.order_by(TablesFinance.rate.desc()).paginate(page=page, per_page=per_page)

    banks_data = [{
        'bank_name': table.financial_agreement.banker.name,
        'agreement_name': table.financial_agreement.name,
        'table_name': table.name,
        'table_code': table.table_code,
        'rate': table.rate
    } for table in tables_paginated.items]

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(banks_data)
    
    return render_template("fynance/controllers_comission.html", banks=banks_data, pagination=tables_paginated)


@bp_fynance.route("/manage-report", methods=['GET'])
@login_required
def manage_report():
    """
        # ?? rota para gerenciar relatorio de comissoes pagas
    """
    return render_template("fynance/manage_report.html", banks=Banker.query.all())


@bp_fynance.route("/manage-payment")
@login_required
def manage_payment():
    """
        # todo função para gerar o pagamento
    """
    return render_template("fynance/manage_payment.html")


@bp_fynance.route("/process-data", methods=['POST'])
@login_required
def process_data():
    """Api`s 
        modular api system within the monolithic, process models report banker comission check
    Returns:
        _type_: _post_
        _data_: _bank and name in database_
    """
    data = request.get_json()
    columns = data.get('columns', [])
    bank_id = data.get('bankID')
    name_report = data.get('name_report')

    if not columns:
        return jsonify({"error": "Dados insuficientes para verificação."}), 400

    data_rows = columns[1:]  # Ignora a primeira linha

    valid_data = []
    invalid_data = []

    proposals = Proposal.query.all()
    tables = TablesFinance.query.filter_by(banker_id=bank_id).all()

    # Mapas para validação rápida
    proposal_cpf_map = {str(proposal.cpf).replace('.', '').replace('-', ''): proposal for proposal in proposals}
    proposal_number_map = {proposal.number_proposal.strip(): proposal for proposal in proposals}
    table_code_map = {table.table_code.strip(): table for table in tables}

    # Verificação das colunas no arquivo
    for row in data_rows:
        cpf = row['CPF'].replace('.', '').replace('-', '')  # Normalizando o CPF
        proposal_number = row['NUMERO_DA_PROPOSTA'].strip()
        table_code = row['CODIGO_DA_TABELA'].strip()

        # Verificação se o CPF, número da proposta e código da tabela correspondem
        proposal_by_cpf = proposal_cpf_map.get(cpf)
        proposal_by_number = proposal_number_map.get(proposal_number)
        table_by_code = table_code_map.get(table_code)

        # Verificar se todos os dados estão corretos
        if proposal_by_cpf and proposal_by_number and proposal_by_cpf == proposal_by_number and table_by_code:
            valid_data.append({ 'CPF': cpf, 'Numero da Proposta': proposal_number, 'Codigo da Tabela': table_code, 'Valor da Operacao': proposal_by_cpf.value_operation})
            # validando o report data com os dados
            new_report = ReportData(report_name=name_report, date_import=datetime.now(), cpf=valid_data.get('CPF'), number_proposal=valid_data.get('Numero da Proposta'), table_code=valid_data.get("Codigo da Tabela"), value_operation=valid_data.get("Valor da Operacao"), is_valid=True)
            db.session.add(new_report)
            db.session.commit()
        
        else:
            # Proposta inválida
            invalid_data.append({ 'CPF': cpf, 'Numero da Proposta': proposal_number, 'Codigo da Tabela': table_code})

    # Se todos os dados forem válidos
    if len(invalid_data) == 0:
        message = f"Todos os dados foram do relatorio de comissões pagas verificados com sucesso!"
    else:
        message = f"Dados inválidos encontrados."

    return jsonify({ "valid_data": valid_data, "invalid_data": invalid_data, "message": message, "total_valid": len(valid_data), "total_invalid": len(invalid_data) }), 200



@bp_fynance.route("/register-convenio", methods=['POST'])
@login_required
def add_register_conven():
    """Api`s 
        modular api system within the monolithic
    Returns:
        _type_: _post_
        _data_: _bank and name in database_
    """
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
def add_register_bankers():
    """Api`s 
        modular api system within the monolithic
    Returns:
        _type_: _post_
        _data_: _bank unique and name in database_
    """
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
                is_status=False,
            )
            db.session.add(new_table)
        db.session.commit()

        return jsonify({"message": "Dados processados com sucesso!"}), 200
    
    except Exception as e:
        print(e)
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
    is_status = False
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
            is_status=is_status
        )
        db.session.add(new_table)
        db.session.commit()
        return redirect(url_for("fynance.gerement_finance"))
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp_fynance.route("/delete-bankers/<int:id>", methods=['POST'])
@login_required
def delete_bankers(id):
    """
        Delete banker associate conv and tables
    """
    banker = Banker.query.get_or_404(id)
    db.session.delete(banker)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Banco deletado com sucesso!'}), 200
    

@bp_fynance.route("/delete-bankers/conv/<int:id>", methods=['POST'])
@login_required
def delete_conv_in_banker(id):
    """Function for delete conv in banker"""
    convenio = FinancialAgreement.query.get_or_404(id)
    db.session.delete(convenio)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Convênio deletado com sucesso!'}), 200


@bp_fynance.route("/delete-bankers/conv/tables/<int:id>", methods=['POST'])
@login_required
def delete_table_in_conv_in_banker(id):
    """Function for delete table in conv in banker"""
    table = TablesFinance.query.get_or_404(id)
    table.is_status = True
    db.session.commit()
    return jsonify({"success": True, 'message': 'Tabela deletada com sucesso!'}), 200


@bp_fynance.route("/clean-tables", methods=['POST'])
@login_required
def disable_tables():
    """
        routes commits for tables for column is_status for true.
    """
    data = request.get_json()
    table_ids = data.get('table_ids', [])

    if not table_ids:
        return jsonify({"success": False, "message": "Nenhuma tabela selecionada."}), 400

    try:
        tables = TablesFinance.query.filter(TablesFinance.id.in_(table_ids)).all()
        if not tables:
            return jsonify({"success": False, "message": "Tabelas não encontradas."}), 404

        for table in tables:
            table.is_status = True
        
        db.session.commit()
        return jsonify({"success": True, "message": "Tabelas desativadas com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Erro ao desativar as tabelas: {str(e)}"}), 500

