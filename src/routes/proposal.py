import os 

from datetime import datetime
from flask_sqlalchemy import pagination
from flask import (Blueprint, render_template, url_for, jsonify, abort, redirect, request, current_app, flash)
from flask_login import login_required, current_user 
from src import db
from werkzeug.utils import secure_filename
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from src.utils.proposal import UploadProposal
from src.models.bsmodels import User, Banker, FinancialAgreement, TablesFinance, UserProposal, Roomns, room_user_association

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
    """ function for create proposal

    Returns:
        proppsal: create 
    """
    bankers = Banker.query.options(
        joinedload(Banker.financial_agreements).joinedload(FinancialAgreement.tables_finance)
    ).order_by(Banker.name).all()
    
    return render_template("proposal/creat_proposal.html", bankers=bankers)



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
        'name_and_lastname': p.name_and_lastname,
        'created_at': p.created_at.strftime('%d/%m/%Y'),
        'cpf': p.cpf,
        'active': p.active,
        'block': p.block,
        'is_status': p.is_status
    } for p in tables_paginated.items]

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(proposal_data)
    
    return render_template("proposal/state_proposal.html", proposal=proposal_data, pagination=tables_paginated)


@bp_proposal.route("/proposal/new-proposal", methods=['POST'])
@login_required
def add_proposal():
    form_data = request.form
    try:
        new_proposal = UserProposal(
            creator_id=current_user.id,
            banker_id=form_data.get('bankSelect'),
            conv_id=form_data.get('convenioSelectProposal'),
            table_id=form_data.get('tableSelectProposal'),
            operation_select=form_data.get('operationselect'),
            matricula=form_data.get('matricula'),
            text_password_server=form_data.get('TextPasswordServer'),
            ddb=datetime.strptime(form_data.get('ddb'), '%Y-%m-%d'),
            passowrd_chek=form_data.get('senhacontracheque'),
            name_and_lastname=form_data.get('nameRegisterProposal'),
            dd_year=datetime.strptime(form_data.get('ddb-year'), '%Y-%m-%d'),
            sex=form_data.get('SexSelect'),
            select_state=form_data.get('stateselect'),
            email=form_data.get('email'),
            cpf=form_data.get('CPF'),
            naturalidade=form_data.get('naturalidade'),
            identify=form_data.get('identidade'),
            organ_emissor=form_data.get('orgao_emissor'),
            uf_emissor=form_data.get('StateUfSelect'),
            day_emissor=datetime.strptime(form_data.get('data_emissao'), '%Y-%m-%d'),
            name_father=form_data.get('father'),
            name_mother=form_data.get('mother'),
            zipcode=form_data.get('zipcode'),
            address=form_data.get('address'),
            address_number=form_data.get('address-number'),
            address_complement=form_data.get('address-complement'),
            neighborhood=form_data.get('neighborhood'),
            city=form_data.get('city'),
            state_uf_city=form_data.get('StateUfCitySelect'),
            value_salary=form_data.get('value-salary'),
            value_salaray_liquid=form_data.get('value-salary-liquid'),
            phone=form_data.get('phone'),
            phone_residential=form_data.get('phone-residential'),
            phone_comercial=form_data.get('phone-comercial'),
            benefit_select=form_data.get('benefitselect'),
            uf_benefit_select=form_data.get('StateBenefitUf'),
            select_banker_payment_type=form_data.get('SelectBankerPaymentType'),
            select_banker_payment=form_data.get('SelectBankerPayment'),
            receivedcardbenefit=form_data.get('receivedCardBenefit'),
            agency_bank=form_data.get('bankPix', None),
            pix_type_key=form_data.get('pixKeyType', None),
            agency=form_data.get('agencyCreditAccounts', None),
            agency_dv=form_data.get('agencyDVCreditAccounts', None),
            account=form_data.get('accountCreditAccounts', None),
            account_dv=form_data.get('accountDVCreditAccounts', None),
            type_account=form_data.get('accountTypeCreditAccounts', None),
            agency_op=form_data.get('agencyOPOrder', None),
            agency_dvop=form_data.get('agencyDVOPOrder', None),
            margem=form_data.get('margem'),
            parcela=form_data.get('parcela'),
            prazo=form_data.get('prazo'),
            value_operation=form_data.get('valor_operacao'),
            obeserve=form_data.get('observacoes')
        )

        db.session.add(new_proposal)
        db.session.flush()

        image_fields = [
            'rg_cnh_completo', 'contracheque', 'extrato_consignacoes',
            'comprovante_residencia', 'selfie', 'comprovante_bancario',
            'detalhamento_inss', 'historico_consignacoes_inss'
        ]

        paths = UploadProposal().create_directory_structure(proposal_id=f"number_contrato_{new_proposal.id}_Digitador_{current_user.id}", image_fields=image_fields)

        for field in image_fields:
            field_files = request.files.getlist(f'{field}[]')
            if field_files:
                image_paths = UploadProposal().save_images(field_files, paths[field])
                setattr(new_proposal, field, ','.join(image_paths))

        db.session.commit()
        return jsonify({'success': True, 'message': 'Contrato registrado com sucesso'}), 200
        # return redirect(url_for("proposal.state_proposal"))

    except Exception as e:
        db.session.rollback()
        print(f"{str(e)}")
        current_app.logger.error("Erro ao processar o formulário: %s", e)
        return jsonify({'error': str(e)}), 500
    
    
@bp_proposal.route("/proposal/edit-proposal/<int:id>", methods=['GET', 'POST'])
@login_required
def state_details(id):
    """Edit proposal"""
    proposal = UserProposal.query.get_or_404(id)

    if request.method == 'POST':
        proposal.name_and_lastname = request.form.get('name_and_lastname')
        proposal.created_at = request.form.get('created_at') 
        proposal.active = 'active' in request.form
        proposal.block = 'block' in request.form
        proposal.is_status = 'is_status' in request.form
        

        db.session.commit()
        flash('Proposta atualizada com sucesso!', 'success')
        return redirect(url_for('proposal.state_proposal'))
    
    return render_template("proposal/edit_proposal.html", proposal=proposal)

@bp_proposal.route("/proposal/rom-selles")
@login_required
def room_proposal():
    user = User.query.filter_by(id=current_user.id).first()

    rooms = Roomns.query.join(room_user_association).filter(room_user_association.c.user_id == user.id).all()

    extension = [room.create_room for room in rooms]
    extension_room = [{"id": room.id, "name": room.create_room} for room in rooms]

    return render_template(
        "proposal/room_proposal.html",
        user=user,
        extension=extension,
        extension_room=extension_room,
    )