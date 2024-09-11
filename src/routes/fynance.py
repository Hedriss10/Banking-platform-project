import pandas as pd
import io
from flask import Blueprint , render_template, request, redirect, url_for, make_response
from flask_login import login_required, current_user
from flask import jsonify
from src import db
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename
from src.models.bsmodels import Banker, FinancialAgreement, TablesFinance, ReportBankerTransactionData, CalcComissionRate, UserProposal

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
    return render_template("fynance/manager_banker.html", banks=bankers)

@bp_fynance.route("/report-banker")
@login_required
def controllers_report_banker_comission():
    """
        Function for adjust comission of banker 
    Returns:
        comission: return render_template bankers 
    """
    bankers = Banker.query.options(
        db.joinedload(Banker.financial_agreements).subqueryload(FinancialAgreement.tables_finance)
    ).order_by(Banker.name).all()
    return render_template("fynance/report_banker.html", banks=bankers)


@bp_fynance.route("/manage-comission")
@login_required
def manage_comission():
    """Function para rank de comissão associando a tabela Flat da coluna TablesFinance"""
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


@bp_fynance.route("/comission-calc", methods=['GET', 'POST'])
def comission_calc():
    """
        Rota para calcular e gerenciar o repasse de comissão.
    """
    bankers = Banker.query.all()
    tables = TablesFinance.query.all()
    proposals = None
    selected_table = None
    calculated_commissions = []

    if request.method == 'POST':
        banker_id = request.form.get('banker_id', type=int)
        table_id = request.form.get('table_id', type=int)
        repasse_percentage = request.form.get('repasse_percentage', type=float)  # Captura o repasse do form

        if not banker_id or not table_id or repasse_percentage is None:
            return jsonify({"error": "Selecione um banco, uma tabela e o percentual de repasse para calcular a comissão."}), 400

        selected_banker = Banker.query.get(banker_id)
        selected_table = TablesFinance.query.get(table_id)

        if not selected_banker or not selected_table:
            return jsonify({"error": "Banco ou tabela de comissão não encontrados."}), 404

        # Buscar a taxa de comissão da tabela TablesBanker
        table_banker = TablesFinance.query.filter_by(banker_id=banker_id).all()
        if not table_banker:
            return jsonify({"error": "Tabela de comissão não encontrada para o banco selecionado."}), 404

        # Buscar as propostas
        proposals = UserProposal.query.filter_by(banker_id=banker_id).all()

        for proposal in proposals:
            # Assumindo que há apenas uma taxa para cada banco, ajuste conforme necessário
            table = next((t for t in table_banker if t.id == selected_table.id), None)
            if not table:
                continue

            valor_comissao = table.rate  # Obtém a taxa da tabela, não da proposta
            rate = float(valor_comissao.replace('%', ''))  # Remove o '%' e converte para float

            # Calcula a comissão a ser repassada
            repasse_comissao = (rate * repasse_percentage) / 100
            cpf = proposal.cpf
            nome_vendedor = proposal.name_and_lastname

            # Salva o cálculo no banco de dados
            calc = CalcComissionRate(
                banker_id=banker_id,
                table_finance_id=table_id,
                proposal_id=proposal.id,
                user_id=proposal.creator_id,
                valor_comissao=valor_comissao,
                repasse_comissao=repasse_comissao,
                percentage_applied=repasse_percentage
            )

            db.session.add(calc)
            db.session.commit()

            calculated_commissions.append({
                "cpf": cpf,
                "valor_comissao": valor_comissao,
                "repasse_comissao": repasse_comissao,
                "nome_vendedor": nome_vendedor,
                "status": "OK"
            })

    return render_template('fynance/manage_comission.html', bankers=bankers, tables=tables, 
                           proposals=proposals, selected_table=selected_table, 
                           calculated_commissions=calculated_commissions)


@bp_fynance.route("/manage-report", methods=['GET'])
def manage_report():
    """Função para gerenciar relatórios"""

    banker_id = request.args.get('banker_id', type=int)
    banks = Banker.query.all()

    manage_report = []
    report_status = []

    if banker_id:
        manage_report = ReportBankerTransactionData.query.filter_by(banker_id=banker_id).all()
        proposals = UserProposal.query.all()
        proposal_cpf_map = {proposal.cpf: proposal for proposal in proposals}

        if not manage_report:
            return render_template("fynance/manage_report.html", 
                                   banks=banks, 
                                   selected_banker_id=banker_id,
                                   message="Nenhum relatório encontrado para o banco selecionado. Cadastre um novo relatório.")

        for report in manage_report:
            data = report.data
            columns = data.get('columns', [])
            valid_columns = [col for col in columns if col.get('CPF') in proposal_cpf_map]
            invalid_columns = [col for col in columns if col.get('CPF') not in proposal_cpf_map]
            status = 'OK' if not invalid_columns else 'Incorreto'

            valid_proposals = [proposal_cpf_map[col['CPF']] for col in valid_columns]

            report_status.append({
                'report_id': report.id,
                'bankID': data.get('bankID'),
                'convID': data.get('convID'),
                'status': status,
                'valid_columns_count': len(valid_columns),
                'invalid_columns_count': len(invalid_columns),
                'valid_columns': valid_columns,
                'valid_proposals': valid_proposals
            })

    return render_template("fynance/manage_report.html", 
                           report_status=report_status, 
                           selected_banker_id=banker_id, 
                           banks=banks)


@bp_fynance.route("/download-report/<int:report_id>", methods=['GET'])
def download_report(report_id):
    """Função para gerar o CSV do relatório com propostas relacionadas"""
    report = ReportBankerTransactionData.query.get(report_id)
    if not report:
        return "Relatório não encontrado", 404

    columns = report.data.get('columns', [])
    df = pd.DataFrame(columns)

    proposals = UserProposal.query.all()
    proposal_cpf_map = {proposal.cpf: proposal for proposal in proposals}

    proposal_names = []
    proposal_emails = []
    proposal_operations = []

    for col in columns:
        cpf = col.get('CPF')
        proposal = proposal_cpf_map.get(cpf)
        if proposal:
            proposal_names.append(proposal.name_and_lastname)
            proposal_emails.append(proposal.email)
            proposal_operations.append(proposal.operation_select)
        else:
            proposal_names.append('N/A')
            proposal_emails.append('N/A')
            proposal_operations.append('N/A')

    df['Nome da Proposta'] = proposal_names
    df['Email da Proposta'] = proposal_emails
    df['Operação da Proposta'] = proposal_operations

    output = io.StringIO()
    df.to_csv(output, index=False, sep=";")
    output.seek(0)

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename=relatorio_{report_id}.csv"
    response.headers["Content-type"] = "text/csv"
    return response


@bp_fynance.route("/controls-box", methods=['GET'])
@login_required
def controllers_box():
    """function for controllers box approved"""
    # Consultar todas as comissões pagas
    paid_commissions = CalcComissionRate.query.all()    
    total_paid = sum(calc.repasse_comissao for calc in paid_commissions)
    print(total_paid)  
    return render_template("fynance/controllers_box.html", total_paid=total_paid)


@bp_fynance.route("/manage-payment")
@login_required
def manage_payment():
    """Function for payment"""
    return render_template("fynance/manage_payment.html")


@bp_fynance.route("/manage-analytics")
@login_required
def manage_analytics():
    """function for analytcis"""
    return render_template("fynance/manage_analytics.html")


@bp_fynance.route("/process-data", methods=['POST'])
@login_required
def process_data():
    """
        Carried out to generate the commission report, dynamically and sent to the bank
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Nenhum dado recebido"}), 400
        
        bank_id = data.get('bankID')
        conv_id = data.get('convID')
        columns = data.get('columns', [])

        column_names = columns[0]
        rows = columns[1:]
        row_list = []

        for row in rows:
            row_data = {column_names[i]: row[i] for i in range(len(row))}
            row_list.append(row_data)
        
        data_to_save = {
            'columns': row_list,
            'bankID': bank_id,
            'convID': conv_id
        }
        new_entry = ReportBankerTransactionData(
            banker_id=bank_id,
            conv_id=conv_id,
            data=data_to_save
        )
        db.session.add(new_entry)
        db.session.commit()

        return jsonify({"message": "Dados processados com sucesso!"}), 200

    except Exception as e:
        print(f"Erro ao processar dados: {e}")
        return jsonify({"error": "Erro ao processar os dados"}), 500


@bp_fynance.route("/register-convenio", methods=['POST'])
@login_required
def post_register_conven():
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
def post_register_bankers():
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
            )
            db.session.add(new_table)
        db.session.commit()

        return jsonify({"message": "Dados processados com sucesso!"}), 200
    
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
    """Function for delete id banker"""
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
    db.session.delete(table)
    db.session.commit()
    return jsonify({"success": True, 'message': 'Tabela deletada com sucesso!'}), 200


@bp_fynance.route("/save-report-template", methods=['GET'])
def save_template_report_comission():
    """
        Coleta todos os dados do relatório e faz associação com o template.
    """
    banker_id = request.args.get('banker_id', type=int)
    conv_id = request.args.get('conv_id', type=int)

    try:
        if not banker_id or not conv_id:
            return jsonify({'error': 'Os campos Banco e Orgão são necessários.'}), 400
        
        report_comission = ReportBankerTransactionData.query.filter_by(
            banker_id=banker_id, 
            conv_id=conv_id
        ).all()
        
        banker = Banker.query.filter_by(id=banker_id).first()
        convenio = FinancialAgreement.query.filter_by(id=conv_id).first()

        if not report_comission:
            return jsonify({'message': 'Nenhum template de relatório encontrado para os parâmetros fornecidos.'}), 404

        templates = [{
            'Último template importado': index + 1,
            'Banco': banker.name if banker else 'Desconhecido',
            'Convênio': convenio.name if convenio else 'Desconhecido',
            'Colunas': report.data.get('columns', []) 
        } for index, report in enumerate(report_comission)]

        return jsonify(templates), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500