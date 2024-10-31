import json

from sqlalchemy.orm import joinedload
from flask import current_app, jsonify, flash, redirect, url_for
from src.models.bsmodels import Proposal, Banker, FinancialAgreement, TablesFinance
from datetime import datetime


def get_nullable_value(value):
    return value if value not in ('', None) else None


class ProposalControllers:
    
    def __init__(self, current_user):
        self.current_user = current_user

    def state_proposal_controllers(self, search_term, page, per_page):
        
        query = Proposal.query.filter_by(creator_id=self.current_user)
        
        if search_term:
            query = query.filter(
                Proposal.name.ilike(f'%{search_term}%') |  # Filtrar pelo nome da proposta
                Proposal.cpf.ilike(f'%{search_term}')      # Filtrar pelo CPF
            )
            
        try:
            created_at_date = datetime.strptime(search_term, '%Y-%m-%d')
            query = query.filter(Proposal.created_at >= created_at_date)
        except ValueError:
            pass

        tables_paginated = query.filter_by(is_status=False).order_by(Proposal.created_at.desc()).paginate(page=page, per_page=per_page)

        proposal_data = [{
            'id': p.id,
            'creator_name': p.creator.username if p.creator else 'Desconhecido',
            'name': p.name,
            'created_at': p.created_at,
            'operation_select': p.operation_select,
            'cpf': p.cpf,
            'aguardando_digitacao': p.aguardando_digitacao,
            'pendente_digitacao': p.pendente_digitacao,
            'contrato_digitacao': p.contrato_digitacao,
            'aguardando_aceite_do_cliente': p.aguardando_aceite_do_cliente,
            'aceite_feito_analise_do_banco': p.aceite_feito_analise_do_banco,
            'contrato_pendente_pelo_banco': p.contrato_pendente_pelo_banco,
            'aguardando_pagamento': p.aguardando_pagamento,
            'contratopago': p.contratopago,
            'edit_at': p.edit_at if p.edit_at else "Ninguem Editou",
            'completed_at': p.completed_at if p.completed_at else "Ninguem Digitou",
            'completed_by': p.completed_by if p.completed_by else "Digitado por"
        } for p in tables_paginated.items]
        
        return proposal_data, tables_paginated
        
    def filter_tables_with_search(self, search_term):
        if search_term:
            tables = TablesFinance.query.filter(TablesFinance.table_code.ilike(f'%{search_term}%')).all()
            results = [{'id': table.id, 'type_table': table.type_table, 'start_term':table.start_term, 'end_term': table.end_term, 
                        'code': table.table_code, 'name': table.name, 'rate': table.rate} for table in tables]
            return jsonify(results)
        return jsonify([])

    def page_create_proposal_controllers(self):
        bankers = Banker.query.options(
            joinedload(Banker.financial_agreements).joinedload(FinancialAgreement.tables_finance)
        ).order_by(Banker.name).all()
        
        return bankers

    def state_tables_finance_controllers(self, search_term, page, per_page):
        bankers = Banker.query.options(
            joinedload(Banker.financial_agreements).joinedload(FinancialAgreement.tables_finance)
        ).order_by(Banker.name).all()
        
        query = TablesFinance.query.join(FinancialAgreement).join(Banker)
        
        if search_term:
            query = query.filter(
                TablesFinance.name.ilike(f'%{search_term}%') |   # Filtro pelo nome da tabela
                TablesFinance.table_code.ilike(f'%{search_term}%') |  # Filtro pelo código da tabela
                Banker.name.ilike(f'%{search_term}%') |   # Filtro pelo nome do banco
                FinancialAgreement.name.ilike(f'%{search_term}%')   # Filtro pelo nome do convênio
                # (TablesFinance.rate == search_rate if search_rate is not None else False)  # Filtro pela taxa de comissão
            )
        
        tables_paginated = query.order_by(TablesFinance.rate.desc()).paginate(page=page, per_page=per_page)
        
        banks_data = [{
            'bank_name': table.financial_agreement.banker.name,
            'agreement_name': table.financial_agreement.name,
            'table_name': table.name,
            'table_code': table.table_code,
            # 'rate': table.rate
        } for table in tables_paginated.items]

        return banks_data, bankers, tables_paginated

    def add_proposal_controllers(self, request , form_data):
        """
            _add proposal controllers_
            def for add controllers proposal in database. 
        Args:
            request (_type_): request of frontend.
            form_data (_type_): form_fata process 

        Returns:
            _type_: _description_
        """
        try:
            new_proposal = Proposal(
            creator_id=self.current_user.id,
            banker_id=get_nullable_value(form_data.get('bankSelect')),
            created_at=datetime.now(),
            conv_id=get_nullable_value(form_data.get('convenioSelectProposal')),
            table_id=get_nullable_value(form_data.get('tableSelectProposal')),
            operation_select=get_nullable_value(form_data.get('operationselect')),
            matricula=get_nullable_value(form_data.get('matricula')),
            passowrd_chek=get_nullable_value(form_data.get('senhacontracheque')),
            name=get_nullable_value(form_data.get('nameRegisterProposal')),
            lastname=get_nullable_value(form_data.get('nameRegisterProposal')),
            date_year=datetime.strptime(get_nullable_value(form_data.get('ddb-year')), '%Y-%m-%d') if form_data.get('ddb-year') else datetime.now(),
            sex=get_nullable_value(form_data.get('SexSelect')),
            select_state=get_nullable_value(form_data.get('stateselect')),
            email=get_nullable_value(form_data.get('email')),
            cpf=get_nullable_value(form_data.get('CPF')),
            naturalidade=get_nullable_value(form_data.get('naturalidade')),
            identify_document=get_nullable_value(form_data.get('identidade')),
            organ_emissor=get_nullable_value(form_data.get('orgao_emissor')),
            uf_emissor=get_nullable_value(form_data.get('StateUfSelect')),
            day_emissor=datetime.strptime(get_nullable_value(form_data.get('data_emissao')), '%Y-%m-%d') if form_data.get('data_emissao') else datetime.now(),
            name_father=get_nullable_value(form_data.get('father')),
            name_mother=get_nullable_value(form_data.get('mother')),
            zipcode=get_nullable_value(form_data.get('zipcode')),
            address=get_nullable_value(form_data.get('address')),
            address_number=get_nullable_value(form_data.get('address-number')),
            address_complement=get_nullable_value(form_data.get('address-complement')),
            neighborhood=get_nullable_value(form_data.get('neighborhood')),
            city=get_nullable_value(form_data.get('city')),
            state_uf_city=form_data.get('StateUfCitySelect', None),
            value_salary=get_nullable_value(form_data.get('value-salary')),
            value_salaray_liquid=get_nullable_value(form_data.get('value-salary-liquid')),
            phone=get_nullable_value(form_data.get('phone')),
            phone_residential=get_nullable_value(form_data.get('phone-residential')),
            phone_comercial=get_nullable_value(form_data.get('phone-comercial')),
            benefit_select=get_nullable_value(form_data.get('benefitselect')),
            uf_benefit_select=get_nullable_value(form_data.get('StateBenefitUf')),
            select_banker_payment_type=get_nullable_value(form_data.get('SelectBankerPaymentType')),
            select_banker_payment=get_nullable_value(form_data.get('SelectBankerPayment')),
            receivedcardbenefit=get_nullable_value(form_data.get('receivedCardBenefit')),
            agency_bank=get_nullable_value(form_data.get('bankPix')),
            pix_type_key=get_nullable_value(form_data.get('pixKeyType')),
            agency=get_nullable_value(form_data.get('agencyCreditAccounts')),
            agency_dv=get_nullable_value(form_data.get('agencyDVCreditAccounts')),
            account=get_nullable_value(form_data.get('accountCreditAccounts')),
            account_dv=get_nullable_value(form_data.get('accountDVCreditAccounts')),
            type_account=get_nullable_value(form_data.get('accountTypeCreditAccounts')),
            agency_op=get_nullable_value(form_data.get('agencyOPOrder')),
            agency_dvop=get_nullable_value(form_data.get('agencyDVOPOrder')),
            margem=get_nullable_value(form_data.get('margem')),
            parcela=get_nullable_value(form_data.get('parcela')),
            prazo=get_nullable_value(form_data.get('prazo')),
            value_operation=float(form_data.get('valor_operacao').strip()) if form_data.get('valor_operacao') and form_data.get('valor_operacao').strip() else 0.0,
            obeserve=get_nullable_value(form_data.get('observacoes')),
            edit_at=get_nullable_value(form_data.get('edit_at')),
            number_proposal=get_nullable_value(form_data.get('number_proposal')),
            pendente_digitacao=1,
            is_status=False)

            image_fields = {
                'rg_cnh_completo': 'image',
                'rg_frente': 'image',
                'rg_verso': 'image',
                'contracheque': 'pdf_or_image',
                'extrato_consignacoes': 'image',
                'comprovante_residencia': 'image',
                'selfie': 'image',
                'comprovante_bancario': 'image',
                'detalhamento_inss': 'image',
                'historico_consignacoes_inss': 'image'
            }
        
            for field in image_fields:
                file = request.files.get(field)
                if file:
                    image_data = file.read()
                    setattr(new_proposal, field, image_data)                    
            
            return new_proposal
        except Exception as e:
            current_app.logger.error(f"Erro ao criar proposta: {e}")
            raise
            
    def edit_proposal_controllers(self, request, id):
            
        bankers = Banker.query.options(joinedload(Banker.financial_agreements).joinedload(FinancialAgreement.tables_finance)).order_by(Banker.name).all()
        proposal = Proposal.query.get_or_404(id)
            
        if proposal.pendente_digitacao == 0:
            flash('Você não pode editar esta proposta. Verifique se ela está bloqueada ou já foi finalizada.', 'danger')
            return redirect(url_for('proposal.state_proposal'))
    
        if request.method == 'POST':
            # proposal.name = request.form.get('name')
            proposal.email = request.form.get('email')
            proposal.date_year = datetime.strptime(request.form.get('date_year'), "%Y-%m-%d").date()
            proposal.sex = request.form.get('sex')
            proposal.phone = request.form.get('phone')
            proposal.address = request.form.get('address')
            proposal.address_number = request.form.get('address_number')
            proposal.zipcode = request.form.get('zipcode')
            proposal.neighborhood = request.form.get('neighborhood')
            proposal.city = request.form.get('city')
            proposal.state_uf_city = request.form.get('state_uf_city')
            proposal.value_salary = request.form.get('value_salary')
            proposal.table_id = request.form.get('tableSelectProposal')
            proposal.conv_id = request.form.get('convenioSelectProposal')
        
        return bankers, proposal
                
    def delete_proposal_controllers(self, id):
        proposal = Proposal.query.get_or_404(id)
        return proposal

    def remove_image_proposal_controllers(self, proposal_id, field):
        proposal = Proposal.query.filter_by(id=proposal_id).first()

        if not proposal:
            return False
        if hasattr(proposal, field):
            setattr(proposal, field, None)
            return True
        return False