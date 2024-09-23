import os 
import base64
import json

from datetime import datetime
from flask import (Blueprint, render_template, url_for, jsonify, abort, redirect, request, current_app, flash)
from flask_login import login_required, current_user 
from src import db
from sqlalchemy.orm import joinedload
from src.utils.proposal import UploadProposal
from src.models.bsmodels import User, Banker, FinancialAgreement, TablesFinance, UserProposal, Roomns, room_user_association
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from src.token.generate_token import load_private_key, get_public_key_str


# derocators api module
bp_proposal = Blueprint("proposal", __name__)


@bp_proposal.route("/proposal")
@login_required
def manage_proposal():
    """Function para rank de comissão associando a tabela Flat da coluna TablesFinance"""
    
    bankers = Banker.query.options(
        joinedload(Banker.financial_agreements).joinedload(FinancialAgreement.tables_finance)
    ).order_by(Banker.name).all()
    
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
    return render_template("proposal/manage_proposal.html", bankers=bankers ,banks=banks_data, pagination=tables_paginated)

@bp_proposal.route("/creat-proposal", methods=['GET'])
@login_required
def creat_proposal():
    """Function to create a proposal."""
    bankers = Banker.query.options(
        joinedload(Banker.financial_agreements).joinedload(FinancialAgreement.tables_finance)
    ).order_by(Banker.name).all()
    public_key_str = get_public_key_str()
    return render_template("proposal/creat_proposal.html", bankers=bankers, public_key=public_key_str)

@bp_proposal.route("/search-tables", methods=['GET'])
@login_required
def search_tables():
    search_term = request.args.get('query', '')
    if search_term:
        tables = TablesFinance.query.filter(TablesFinance.table_code.ilike(f'%{search_term}%')).all()
        results = [{'id': table.id, 'type_table': table.type_table, 'start_term':table.start_term, 'end_term': table.end_term, 
                    'code': table.table_code, 'name': table.name, 'rate': table.rate} for table in tables]
        return jsonify(results)
    return jsonify([])

@bp_proposal.route("/proposal-status")
@login_required
def state_proposal():
    """
        state proposal
        return state proposal status actual
    Returns:
        _type_:  return state proposal
    """
    query = UserProposal.query.filter_by(creator_id=current_user.id)
    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search_term = request.args.get('search', '').lower()
    
    try:
        search_rate = float(search_term)
    except ValueError:
        search_rate = None

    if search_term:
        query = query.filter(
            UserProposal.name_and_lastname.ilike(f'%{search_term}%') |  # Filtrar pelo o nome da campanha
            UserProposal.created_at.ilike(f'%{search_term}%') |# Filtro pelo código da tabela
            UserProposal.cpf.ilike(f'%{search_term}') #  filtrando pelo o cpf do contrato
        )

    
    tables_paginated = query.order_by(UserProposal.created_at.desc()).paginate(page=page, per_page=per_page)

    proposal_data = [{
        'id': p.id,
        'creator_name': p.creator.username if p.creator else 'Desconhecido',
        'name_and_lastname': p.name_and_lastname,
        'created_at': p.created_at,
        'operation_select': p.operation_select,
        'cpf': p.cpf,
        'active': p.active,
        'block': p.block,
        'is_status': p.is_status,
        'progress_check': p.progress_check,
        'edit_at': p.edit_at if p.edit_at else "Esperando Digitação"
    } for p in tables_paginated.items]

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(proposal_data)
    
    return render_template("proposal/state_proposal.html", proposal=proposal_data, pagination=tables_paginated)


@bp_proposal.route("/proposal/new-proposal", methods=['POST'])
@login_required
def add_proposal():
    encrypted_data = request.form.get('encrypted_data')
    encrypted_key = request.form.get('encrypted_key')
    iv_base64 = request.form.get('iv')

    if not encrypted_data or not encrypted_key or not iv_base64:
        return jsonify({'error': 'Dados criptografados faltando'}), 400

    try:
        aes_key = load_private_key().decrypt(
            base64.b64decode(encrypted_key),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    except Exception as e:
        current_app.logger.error(f"Erro ao descriptografar a chave AES: {e}")
        return jsonify({'error': 'Erro ao descriptografar a chave AES'}), 400

    try:
        encrypted_data_bytes = base64.b64decode(encrypted_data)
        iv = base64.b64decode(iv_base64)

        aesgcm = AESGCM(aes_key)
        data_bytes = aesgcm.decrypt(iv, encrypted_data_bytes, None)

        json_string = data_bytes.decode('utf-8')
        form_data = json.loads(json_string)
        
    except Exception as e:
        current_app.logger.error(f"Erro ao descriptografar os dados: {e}")
        return jsonify({'error': 'Erro ao descriptografar os dados do formulário'}), 400
    

    try:
        new_proposal = UserProposal(
        creator_id=current_user.id,
        banker_id=form_data.get('bankSelect', None),
        conv_id=form_data.get('convenioSelectProposal', None),
        table_id=form_data.get('tableSelectProposal', None),
        operation_select=form_data.get('operationselect', None),
        matricula=form_data.get('matricula', None),
        text_password_server=form_data.get('TextPasswordServer', None),
        passowrd_chek=form_data.get('senhacontracheque', None),
        name_and_lastname=form_data.get('nameRegisterProposal', None),
        dd_year=datetime.strptime(form_data.get('ddb-year'), '%Y-%m-%d') if form_data.get('ddb-year') else datetime.now(),
        sex=form_data.get('SexSelect', None),
        select_state=form_data.get('stateselect', None),
        email=form_data.get('email', None),
        cpf=form_data.get('CPF', None),
        naturalidade=form_data.get('naturalidade', None),
        identify=form_data.get('identidade', None),
        organ_emissor=form_data.get('orgao_emissor', None),
        uf_emissor=form_data.get('StateUfSelect'),
        day_emissor = datetime.strptime(form_data.get('data_emissao'), '%Y-%m-%d') if form_data.get('data_emissao') else datetime.now(),
        name_father=form_data.get('father', None),
        name_mother=form_data.get('mother', None),
        zipcode=form_data.get('zipcode', None),
        address=form_data.get('address', None),
        address_number=form_data.get('address-number', None),
        address_complement=form_data.get('address-complement', None),
        neighborhood=form_data.get('neighborhood', None),
        city=form_data.get('city', None),
        state_uf_city=form_data.get('StateUfCitySelect', None),
        value_salary=form_data.get('value-salary', None),
        value_salaray_liquid=form_data.get('value-salary-liquid', None),
        phone=form_data.get('phone', None),
        phone_residential=form_data.get('phone-residential', None),
        phone_comercial=form_data.get('phone-comercial', None),
        benefit_select=form_data.get('benefitselect', None),
        uf_benefit_select=form_data.get('StateBenefitUf', None),
        select_banker_payment_type=form_data.get('SelectBankerPaymentType', None),
        select_banker_payment=form_data.get('SelectBankerPayment', None),
        receivedcardbenefit=form_data.get('receivedCardBenefit', None),
        agency_bank=form_data.get('bankPix', None),
        pix_type_key=form_data.get('pixKeyType', None),
        agency=form_data.get('agencyCreditAccounts', None),
        agency_dv=form_data.get('agencyDVCreditAccounts', None),
        account=form_data.get('accountCreditAccounts', None),
        account_dv=form_data.get('accountDVCreditAccounts', None),
        type_account=form_data.get('accountTypeCreditAccounts', None),
        agency_op=form_data.get('agencyOPOrder', None),
        agency_dvop=form_data.get('agencyDVOPOrder', None),
        margem=form_data.get('margem', None),
        parcela=form_data.get('parcela', None),
        prazo=form_data.get('prazo', None),
        value_operation=form_data.get('valor_operacao', None),
        obeserve=form_data.get('observacoes', None),
        edit_at=form_data.get('', None))

                
        db.session.add(new_proposal)
        db.session.flush()

        image_fields = ['rg_cnh_completo', 'rg_frente', 'rg_verso', 'contracheque', 'extrato_consignacoes','comprovante_residencia', 'selfie', 'comprovante_bancario','detalhamento_inss', 'historico_consignacoes_inss']
        paths = UploadProposal(proposal_id=new_proposal.id, creator_id=current_user.id, image_fields=image_fields, created_at=new_proposal.created_at).create_directory_structure()
        
        for field in image_fields:
            field_files = request.files.getlist(field)
            print(field_files)
            if field_files:
                image_paths = UploadProposal(proposal_id=new_proposal.id, creator_id=current_user.id, image_fields=image_fields, created_at=new_proposal.created_at).save_images(field_files, paths[field])
                setattr(new_proposal, field.rstrip(''), ','.join(image_paths))

        db.session.commit()
        return jsonify({'success': True, 'message': 'Contrato registrado com sucesso'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Erro ao processar o formulário: %s", e)
        return jsonify({'error': str(e)}), 500


@bp_proposal.route("/proposal/edit-proposal/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_proposal(id):
    proposal= UserProposal.query.get_or_404(id) 
        
    if proposal.active != 0 or proposal.block != 0 or proposal.is_status != 0:
        flash('Você não pode editar esta proposta. Verifique se ela está bloqueada ou já foi finalizada.', 'danger')
        return redirect(url_for('proposal.state_proposal'))
    
    image_fields = ['rg_cnh_completo', 'contracheque', 'rg_frente', 'rg_verso', 'extrato_consignacoes', 'comprovante_residencia', 'selfie', 'comprovante_bancario', 'detalhamento_inss', 'historico_consignacoes_inss']

    if isinstance(proposal.created_at, str):
        proposal.created_at = datetime.strptime(proposal.created_at, "%Y-%m-%d %H:%M:%S")

    image_paths = UploadProposal(proposal_id=proposal.id, creator_id=proposal.creator_id, image_fields=image_fields, created_at=proposal.created_at).list_images()

    if request.method == 'POST':
        proposal.name_and_lastname = request.form.get('name_and_lastname')
        proposal.email = request.form.get('email')
        proposal.cpf = request.form.get('cpf')
        proposal.sex = request.form.get('sex')
        proposal.phone = request.form.get('phone')
        proposal.address = request.form.get('address')
        proposal.zipcode = request.form.get('zipcode')
        proposal.neighborhood = request.form.get('neighborhood')
        proposal.city = request.form.get('city')
        proposal.state_uf_city = request.form.get('state_uf_city')
        proposal.value_salary = request.form.get('value_salary')
        proposal.obeserve = request.form.get('obeserve')
        
        identifier = f"number_contrato_{proposal.id}_digitador_{proposal.creator_id}"

        base_path = os.path.join('proposta', proposal.created_at.strftime('%Y'), proposal.created_at.strftime('%m'), proposal.created_at.strftime('%d'), identifier)

        for field in image_fields:
            field_files = request.files.getlist(field)
            if field_files:
                field_base_path = os.path.join(base_path, field)
                image_paths = UploadProposal().save_images(field_files, field_base_path)
                setattr(proposal, field, ','.join(image_paths))
        
        db.session.commit()

        flash('Proposta atualizada com sucesso!', 'success')
        return redirect(url_for('proposal.state_proposal'))

    return render_template("proposal/edit_proposal.html", proposal=proposal, image_paths=image_paths)
    
    
@bp_proposal.route("/proposal/delete-proposal/<int:id>", methods=['GET', 'POST'])
@login_required
def delete_proposal(id):
    """
        Função para deletar proposta e remover os arquivos relacionados.
    """
    proposal = UserProposal.query.get_or_404(id)
    
    image_fields = ['rg_cnh_completo', 'contracheque', 'rg_frente', 'rg_verso', 'extrato_consignacoes', 'comprovante_residencia', 'selfie', 'comprovante_bancario', 'detalhamento_inss', 'historico_consignacoes_inss']
    
    try:
        if isinstance(proposal.created_at, str):
            proposal.created_at = datetime.strptime(proposal.created_at, "%Y-%m-%d %H:%M:%S")
        
        image_paths = UploadProposal(proposal_id=proposal.id, creator_id=proposal.creator_id, image_fields=image_fields, created_at=proposal.created_at).list_images()
        
        for field, paths in image_paths.items():
            for path in paths:
                full_path = os.path.join('proposta', path)
                if os.path.exists(full_path):
                    os.remove(full_path)

        db.session.delete(proposal)
        db.session.commit()

        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao excluir a proposta: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500