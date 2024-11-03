import base64

from flask import current_app
from src import db
from sqlalchemy import desc
from sqlalchemy.orm import joinedload
from src.models.bsmodels import Proposal, Banker, FinancialAgreement
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError


class OperationalControllers:
    
    def __init__(self, current_user):
        self.current_user = current_user
        
    def manage_list_contract_controllers(self):
        ...
    
    def manage_operational_controllers(self, page, per_page):

        proposal_board = {
            "pendente_digitacao": Proposal.query.filter_by(pendente_digitacao=1, is_status=False).count(),
            "aguardando_digitacao": Proposal.query.filter_by(aguardando_digitacao=1, is_status=False).count(),
            "contrato_digitacao": Proposal.query.filter_by(contrato_digitacao=1, is_status=False).count(),
            "aguardando_aceite": Proposal.query.filter_by(aguardando_aceite_do_cliente=1, is_status=False).count(),
            "aceite_analise_banco": Proposal.query.filter_by(aceite_feito_analise_do_banco=1, is_status=False).count(),
            "pendente_banco": Proposal.query.filter_by(contrato_pendente_pelo_banco=1, is_status=False).count(),
            "contratopago": Proposal.query.filter_by(contratopago=1, is_status=False).count(),
            "contratoexcluido": Proposal.query.filter_by(is_status=True).count()
        }

        proposals_pendente_digitacao = Proposal.query.filter_by(
            pendente_digitacao=1, is_status=False).order_by(
            desc(Proposal.pendente_digitacao)).paginate(page=page, per_page=per_page, error_out=False)

        proposals_aguardando_digitacao = Proposal.query.filter_by(
            aguardando_digitacao=1, is_status=False).order_by(
            desc(Proposal.aguardando_digitacao)).paginate(page=page, per_page=per_page, error_out=False)

        proposals_contrato_digitacao = Proposal.query.filter_by(
            contrato_digitacao=1, is_status=False).order_by(
            desc(Proposal.contrato_digitacao)).paginate(page=page, per_page=per_page, error_out=False)

        proposals_aguardando_aceite_do_cliente = Proposal.query.filter_by(
            aguardando_aceite_do_cliente=1, is_status=False).order_by(
            desc(Proposal.aguardando_aceite_do_cliente)).paginate(page=page, per_page=per_page, error_out=False)

        proposals_aceite_feito_analise_do_banco = Proposal.query.filter_by(
            aceite_feito_analise_do_banco=1, is_status=False).order_by(
            desc(Proposal.aceite_feito_analise_do_banco)).paginate(page=page, per_page=per_page, error_out=False)

        proposals_contrato_pendente_pelo_banco = Proposal.query.filter_by(
            contrato_pendente_pelo_banco=1, is_status=False).order_by(
            desc(Proposal.contrato_pendente_pelo_banco)).paginate(page=page, per_page=per_page, error_out=False)

        proposals_contratopago = Proposal.query.filter_by(
            contratopago=1, is_status=False).order_by(
            desc(Proposal.contratopago)).paginate(page=page, per_page=per_page, error_out=False)

        proposals_delete = Proposal.query.filter_by(
            is_status=True).order_by(
            desc(Proposal.is_status)).paginate(page=page, per_page=per_page, error_out=False)

        return {
            "proposal_board": proposal_board,
            "proposals_pendente_digitacao": proposals_pendente_digitacao,
            "proposals_aguardando_digitacao": proposals_aguardando_digitacao,
            "proposals_contrato_digitacao": proposals_contrato_digitacao,
            "proposals_aguardando_aceite_do_cliente": proposals_aguardando_aceite_do_cliente,
            "proposals_aceite_feito_analise_do_banco": proposals_aceite_feito_analise_do_banco,
            "proposals_contrato_pendente_pelo_banco": proposals_contrato_pendente_pelo_banco,
            "proposals_contratopago": proposals_contratopago,
            "proposals_delete": proposals_delete
        }

    def manage_state_contract_controllers(self, page, per_page, search_term):
        
        query = Proposal.query
        
        try:
            search_rate = float(search_term)
        except ValueError:
            search_rate = None

        if search_term:
            query = query.filter(
                Proposal.name.ilike(f'%{search_term}%') |  # Filtra pelo nome do contrato
                Proposal.created_at.ilike(f'%{search_term}%') |  # Filtra pela data de criação
                Proposal.cpf.ilike(f'%{search_term}%')  # Filtra pelo CPF do contrato
            )
            
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
            'edit_at': p.edit_at if p.edit_at else "Não foi editado ainda",
            'completed_at': p.completed_at if p.completed_at else "Não foi digitado",
            'completed_by': p.completed_by if p.completed_by else "Digitador por"
        } for p in tables_paginated.items]
        
        return proposal_data, tables_paginated
     
    def available_contract_count_controllers(self):
        available_count = Proposal.query.filter_by(pendente_digitacao=True, is_status=False).count()
        return available_count
    
    def manage_edit_contract_controllers(self, proposal_id, request):

        proposal = Proposal.query.get_or_404(proposal_id)
        bankers = Banker.query.options(joinedload(Banker.financial_agreements).joinedload(FinancialAgreement.tables_finance)).order_by(Banker.name).all()

        # Ensure proposal fields are not None
        fields = ["email", "sex", "phone", "address", "address_number", "zipcode", "neighborhood", 
                "city", "state_uf_city", "value_salary", "select_banker_payment_type", 
                "select_banker_payment", "value_operation", "operation_select", "obeserve", "pix_type_key"]
      
        for field in fields:
            setattr(proposal, field, getattr(proposal, field) or "")

        # Encode image fields in base64 for rendering
        image_paths = {field: (base64.b64encode(getattr(proposal, field)).decode('utf-8') if getattr(proposal, field) else None) for field in ['rg_cnh_completo', 'rg_frente', 'rg_verso', 'contracheque',  'extrato_consignacoes', 'comprovante_residencia', 'selfie',  'comprovante_bancario', 'detalhamento_inss', 'historico_consignacoes_inss' ]}

        if request.method == 'POST':
            proposal_fields = {
                'email': 'email', 'date_year': 'date_year', 'sex': 'sex', 'phone': 'phone',
                'address': 'address', 'address_number': 'address_number', 'zipcode': 'zipcode',
                'neighborhood': 'neighborhood', 'city': 'city', 'state_uf_city': 'state_uf_city',
                'value_salary': 'value_salary', 'table_id': 'tableSelectProposal', 'conv_id': 'convenioSelectProposal', 'value_operation' : 'value_operation'
            }
            for field, form_key in proposal_fields.items():
                value = request.form.get(form_key)
                if form_key == 'date_year' and value:
                    value = datetime.strptime(value, "%Y-%m-%d").date()
                setattr(proposal, field, value)

            status_fields = [
                'aguardando_digitacao', 'pendente_digitacao', 'contrato_digitacao', 
                'aguardando_aceite_do_cliente', 'aceite_feito_analise_do_banco', 
                'contrato_pendente_pelo_banco', 'aguardando_pagamento', 'contratopago'
            ]
            for field in status_fields:
                setattr(proposal, field, field in request.form)

            proposal.edit_at = datetime.now()
            db.session.commit()

        return bankers, proposal, image_paths

    def manage_delete_contract_controllers(self, id):

        try:
            proposal = Proposal.query.get_or_404(id)
            db.session.delete(proposal)
            db.session.commit()
            return {'success': True}
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao excluir a proposta: {e}")
            return {'success': False, 'error': str(e)}
    
    def manage_details_contract_controllers(self, proposal_id, request):
        proposal = Proposal.query.get_or_404(proposal_id)
        bankers = Banker.query.options(joinedload(Banker.financial_agreements)
                                    .joinedload(FinancialAgreement.tables_finance)).order_by(Banker.name).all()

        # Convert `created_at` to datetime if it's a string
        if isinstance(proposal.created_at, str):
            proposal.created_at = datetime.strptime(proposal.created_at, "%Y-%m-%d %H:%M:%S")

        # Update fields if the request is POST
        if request.method == 'POST':
            proposal.active = 'active' in request.form
            proposal.number_proposal = request.form.get("number_proposal")

            # Status update fields
            status_fields = [
                'aguardando_digitacao', 'pendente_digitacao', 'contrato_digitacao',
                'aguardando_aceite_do_cliente', 'aceite_feito_analise_do_banco',
                'contrato_pendente_pelo_banco', 'aguardando_pagamento', 'contratopago'
            ]
            for field in status_fields:
                setattr(proposal, field, field in request.form)

            proposal.completed_at = datetime.now()
            proposal.completed_by = f"Digitado por: {self.current_user.username}"
            db.session.commit()

            return True, bankers, proposal  # Indicate that a successful POST operation occurred

        return False, bankers, proposal
        
    def remove_image_controllers(self, proposal_id, field):
        proposal = Proposal.query.filter_by(id=proposal_id).first()

        if not proposal:
            return False
        if hasattr(proposal, field):
            setattr(proposal, field, None)
            return True
        return False