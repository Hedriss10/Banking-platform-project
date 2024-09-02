import os 

from datetime import datetime
from flask_sqlalchemy import pagination
from flask import (Blueprint, render_template, url_for, jsonify, abort, redirect, request, current_app)
from flask_login import login_required, current_user 
from src import db
from werkzeug.utils import secure_filename
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from src.utils.proposal import UploadProposal
from src.models.proposal import UserProposal
from src.models.fynance import Banker, FinancialAgreement, TablesFinance



bp_proposal = Blueprint("proposal", __name__)


@bp_proposal.route("/proposal")
@login_required
def manage_proposal():
    bankers = Banker.query.options(
        joinedload(Banker.financial_agreements).joinedload(FinancialAgreement.tables_finance)
    ).order_by(Banker.name).all()
    return render_template("proposal/manage_proposal.html", bankers=bankers)


@bp_proposal.route('/proposal/status', methods=['GET', 'POST'])
def get_status_proposal():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = UserProposal.query.order_by(UserProposal.name_and_lastname.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template("proposal/state_proposal.html", proposals=pagination.items, pagination=pagination)


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

        paths = UploadProposal().create_directory_structure(proposal_id=f"Número do contrato -> {new_proposal.id}", image_fields=image_fields)

        for field in image_fields:
            field_files = request.files.getlist(f'{field}[]')
            if field_files:
                image_paths = UploadProposal().save_images(field_files, paths[field])
                setattr(new_proposal, field, ','.join(image_paths))

        db.session.commit()
        # return jsonify({'success': True, 'message': 'Contrato registrado com sucesso'})
        return redirect(url_for('overview.home'))

    except Exception as e:
        db.session.rollback()
        print(f"{str(e)}")
        current_app.logger.error("Erro ao processar o formulário: %s", e)
        return jsonify({'error': str(e)}), 500