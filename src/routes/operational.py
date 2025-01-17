# import os

# from flask_sqlalchemy import pagination
# from flask import (Blueprint, render_template, url_for, jsonify, abort, redirect, request, current_app, flash, send_from_directory)
# from flask_login import login_required, current_user 
# from src import db
# from sqlalchemy.orm import joinedload
# from src.models.bsmodels import Proposal, Banker, FinancialAgreement
# from src.utils.proposal import UploadProposal
# from datetime import datetime
# from sqlalchemy import desc


# bp_operational = Blueprint("operational", __name__)

# @bp_operational.route("/list-operational-contract")
# @login_required
# def manage_list_contract():    
#     return render_template("operational/manage_list.html")


# @bp_operational.route("/manage-operational")
# @login_required
# def manage_operational():
#     """"
#         sumary_line
#         filtered and sorted proposal board sorted by creation date
#     Keyword arguments:
#     argument -- description
#     return - proposal filter_by
#     """
#     page = request.args.get('page', 1, type=int)
#     per_page = 10 

#     proposal_board = {
#         "pendente_digitacao": Proposal.query.filter_by(pendente_digitacao=1, is_status=False).count(),
#         "aguardando_digitacao": Proposal.query.filter_by(aguardando_digitacao=1, is_status=False).count(),
#         "contrato_digitacao": Proposal.query.filter_by(contrato_digitacao=1, is_status=False).count(),
#         "aguardando_aceite": Proposal.query.filter_by(aguardando_aceite_do_cliente=1, is_status=False).count(),
#         "aceite_analise_banco": Proposal.query.filter_by(aceite_feito_analise_do_banco=1, is_status=False).count(),
#         "pendente_banco": Proposal.query.filter_by(contrato_pendente_pelo_banco=1, is_status=False).count(),
#         "contratopago": Proposal.query.filter_by(contratopago=1, is_status=False).count(),
#         "contratoexcluido": Proposal.query.filter_by(is_status=True).count()
#     }

#     proposals_pendente_digitacao = Proposal.query.filter_by(pendente_digitacao=1, is_status=False).order_by(desc(Proposal.pendente_digitacao)).paginate(page=page, per_page=per_page, error_out=False)
#     proposals_aguardando_digitacao = Proposal.query.filter_by(aguardando_digitacao=1, is_status=False).order_by(desc(Proposal.aguardando_digitacao)).paginate(page=page, per_page=per_page, error_out=False)
#     proposals_contrato_digitacao = Proposal.query.filter_by(contrato_digitacao=1, is_status=False).order_by(desc(Proposal.contrato_digitacao)).paginate(page=page, per_page=per_page, error_out=False)
#     proposals_aguardando_aceite_do_cliente = Proposal.query.filter_by(aguardando_aceite_do_cliente=1, is_status=False).order_by(desc(Proposal.aguardando_aceite_do_cliente)).paginate(page=page, per_page=per_page, error_out=False)
#     proposals_aceite_feito_analise_do_banco = Proposal.query.filter_by(aceite_feito_analise_do_banco=1, is_status=False).order_by(desc(Proposal.aceite_feito_analise_do_banco)).paginate(page=page, per_page=per_page, error_out=False)
#     proposals_contrato_pendente_pelo_banco = Proposal.query.filter_by(contrato_pendente_pelo_banco=1, is_status=False).order_by(desc(Proposal.contrato_pendente_pelo_banco)).paginate(page=page, per_page=per_page, error_out=False)
#     proposals_contratopago = Proposal.query.filter_by(contratopago=1, is_status=False).order_by(desc(Proposal.contratopago)).paginate(page=page, per_page=per_page, error_out=False)
    
#     proposals_delete = Proposal.query.filter_by(is_status=1).order_by(desc(Proposal.is_status)).paginate(page=10, per_page=per_page, error_out=False)

#     proposals_delete = Proposal.query.filter_by(is_status=True).order_by(desc(Proposal.is_status)).paginate(page=page, per_page=per_page, error_out=False)

#     return render_template("operational/manage_operational.html",  
#                            proposal_board=proposal_board, 
#                            proposals_pendente_digitacao=proposals_pendente_digitacao, 
#                            proposals_aguardando_digitacao=proposals_aguardando_digitacao,  
#                            proposals_contrato_digitacao=proposals_contrato_digitacao, 
#                            proposals_aguardando_aceite_do_cliente=proposals_aguardando_aceite_do_cliente, 
#                            proposals_aceite_feito_analise_do_banco=proposals_aceite_feito_analise_do_banco,
#                            proposals_contrato_pendente_pelo_banco=proposals_contrato_pendente_pelo_banco, 
#                            proposals_contratopago=proposals_contratopago, 
#                            proposals_delete=proposals_delete)


# @bp_operational.route("/state-contract")
# @login_required
# def manage_state_contract():
#     """
#         Function for listing all proposals in the table
#     """
    
#     query = Proposal.query
    
#     page = request.args.get('page', 1, type=int)
#     per_page = 10
#     search_term = request.args.get('search', '').lower()
    
#     try:
#         search_rate = float(search_term)
#     except ValueError:
#         search_rate = None

#     if search_term:
#         query = query.filter(
#             Proposal.name.ilike(f'%{search_term}%') |  # Filtra pelo nome do contrato
#             Proposal.created_at.ilike(f'%{search_term}%') |  # Filtra pela data de criação
#             Proposal.cpf.ilike(f'%{search_term}%')  # Filtra pelo CPF do contrato
#         )
    
#     tables_paginated = query.filter_by(is_status=False).order_by(Proposal.created_at.desc()).paginate(page=page, per_page=per_page)

#     proposal_data = [{
#         'id': p.id,
#         'creator_name': p.creator.username if p.creator else 'Desconhecido',
#         'name': p.name,
#         'created_at': p.created_at,
#         'operation_select': p.operation_select,
#         'cpf': p.cpf,
#         'aguardando_digitacao': p.aguardando_digitacao,
#         'pendente_digitacao': p.pendente_digitacao,
#         'contrato_digitacao': p.contrato_digitacao,
#         'aguardando_aceite_do_cliente': p.aguardando_aceite_do_cliente,
#         'aceite_feito_analise_do_banco': p.aceite_feito_analise_do_banco,
#         'contrato_pendente_pelo_banco': p.contrato_pendente_pelo_banco,
#         'aguardando_pagamento': p.aguardando_pagamento,
#         'contratopago': p.contratopago,
#         'edit_at': p.edit_at if p.edit_at else "Não foi editado ainda",
#         'completed_at': p.completed_at if p.completed_at else "Não foi digitado",
#         'completed_by': p.completed_by if p.completed_by else "Digitador por"
#     } for p in tables_paginated.items]

    
#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         return jsonify(proposal_data)
    
#     return render_template("operational/state_contract.html", proposal=proposal_data, pagination=tables_paginated)


# @bp_operational.route('/operational/available-contracts-count', methods=['GET'])
# @login_required
# def available_contracts_count():
#     available_count = Proposal.query.filter_by(pendente_digitacao=1, is_status=False).count()
    
#     return jsonify({'available_contracts': available_count})


# @bp_operational.route("/operational/edit-proposal/<int:id>", methods=['GET', 'POST'])
# @login_required
# def manage_edit_contract(id):
#     """
#         edit proposal
#     """
#     proposal = Proposal.query.get_or_404(id)
#     bankers = Banker.query.options(joinedload(Banker.financial_agreements).joinedload(FinancialAgreement.tables_finance)).order_by(Banker.name).all()
    
#     image_fields = ['rg_cnh_completo', 'contracheque', 'rg_frente', 'rg_verso', 'extrato_consignacoes', 'comprovante_residencia', 'selfie', 'comprovante_bancario', 'detalhamento_inss', 'historico_consignacoes_inss']

#     upload_manager = UploadProposal(proposal_id=proposal.id, creator_id=proposal.creator_id, image_fields=image_fields, created_at=proposal.created_at)
    
#     # Certifique-se de que a estrutura de diretórios está criada
#     upload_manager.create_directory_structure()

#     image_paths = upload_manager.list_images()

#     if request.method == 'POST':
#         proposal.name = request.form.get('name')
#         proposal.email = request.form.get('email')
#         proposal.date_year = datetime.strptime(request.form.get('date_year'), "%Y-%m-%d").date()
#         proposal.sex = request.form.get('sex')
#         proposal.phone = request.form.get('phone')
#         proposal.address = request.form.get('address')
#         proposal.address_number = request.form.get('address_number')
#         proposal.zipcode = request.form.get('zipcode')
#         proposal.neighborhood = request.form.get('neighborhood')
#         proposal.city = request.form.get('city')
#         proposal.state_uf_city = request.form.get('state_uf_city')
#         proposal.value_salary = request.form.get('value_salary')
#         proposal.obeserve = request.form.get('obeserve')
        
#         proposal.aguardando_digitacao = 'aguardando_digitacao' in request.form
#         proposal.pendente_digitacao = 'pendente_digitacao' in request.form
#         proposal.contrato_digitacao =  'contrato_digitacao' in request.form
#         proposal.aguardando_aceite_do_cliente = 'aguardando_aceite_do_cliente' in request.form
#         proposal.aceite_feito_analise_do_banco = 'aceite_feito_analise_do_banco' in request.form
#         proposal.contrato_pendente_pelo_banco = 'contrato_pendente_pelo_banco' in request.form
#         proposal.aguardando_pagamento = 'aguardando_pagamento' in request.form
#         proposal.contratopago = 'contratopago' in request.form
        
#         identifier = f"number_contrato_{proposal.id}_digitador_{proposal.creator_id}"
#         base_path = os.path.join('proposta', proposal.created_at.strftime('%Y'), proposal.created_at.strftime('%m'), proposal.created_at.strftime('%d'), identifier)

#         for field in image_fields:
#             field_files = request.files.getlist(field)
            
#             if field_files:
#                 field_base_path = os.path.join(base_path, field)
#                 new_images = upload_manager.save_images(field_files, field_base_path)
#                 existing_images = getattr(proposal, field, '').split(',')
#                 all_images = existing_images + new_images
#                 setattr(proposal, field, ','.join([img for img in all_images if img]))
        
#         proposal.edit_at = datetime.now()
#         db.session.commit()
#         return redirect(url_for('operational.manage_state_contract'))

#     return render_template("operational/edit_contract.html", bankers=bankers, proposal=proposal, image_paths=image_paths)


# @bp_operational.route('/proposal/<path:filename>')
# @login_required
# def serve_image(filename):
#     """Serve a imagem da proposta."""
#     base_dir = os.path.join(os.getcwd(), 'proposta')

#     full_path = os.path.join(base_dir, filename)

#     if not os.path.exists(full_path):
#         print(f"Caminho não encontrado: {full_path}")
#         return abort(404)

#     if not os.path.isfile(full_path):
#         print(f"O caminho não é um arquivo: {full_path}")
#         return abort(404)

#     try:
#         directory = os.path.dirname(full_path)
#         file_name = os.path.basename(full_path)
#         return send_from_directory(directory, file_name)
#     except Exception as e:
#         print(f"Erro ao servir a imagem: {e}")
#         return abort(500)


# @bp_operational.route('/operational/delete-proposal/<int:id>', methods=['POST'])
# @login_required
# def manage_delete_contract(id):
#     """
#         Função para deletar proposta e remover os arquivos relacionados.
#     """
#     proposal = Proposal.query.get_or_404(id)
    
#     image_fields = ['rg_cnh_completo', 'contracheque', 'rg_frente', 'rg_verso', 'extrato_consignacoes', 'comprovante_residencia', 'selfie', 'comprovante_bancario', 'detalhamento_inss', 'historico_consignacoes_inss']
    
#     try:
#         if isinstance(proposal.created_at, str):
#             proposal.created_at = datetime.strptime(proposal.created_at, "%Y-%m-%d %H:%M:%S")
        
#         year = proposal.created_at.strftime("%Y")
#         month = proposal.created_at.strftime("%m")
#         day = proposal.created_at.strftime("%d")
#         identifier = f"number_contrato_{proposal.id}_digitador_{proposal.creator_id}"
#         base_path = os.path.join('proposta', year, month, day, identifier)

#         for field in image_fields:
#             field_path = os.path.join(base_path, field)
#             if os.path.exists(field_path):
#                 for img_file in os.listdir(field_path):
#                     full_image_path = os.path.join(field_path, img_file)
#                     if os.path.isfile(full_image_path):
#                         os.remove(full_image_path)
#                 os.rmdir(field_path)

#         if os.path.exists(base_path):
#             os.rmdir(base_path)

#         proposal.is_status = True
#         proposal.deleted_at = f"""Excluido por: {current_user.username}"""
#         db.session.commit()

#         return jsonify({'success': True}), 200
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error(f"Erro ao excluir a proposta: {e}")
#         return jsonify({'success': False, 'error': str(e)}), 500


# @bp_operational.route('/operational/details/<int:id>', methods=['GET', 'POST'])
# @login_required
# def manage_details_contract(id):
#     """
#         Editar proposta
#     """
#     proposal = Proposal.query.get_or_404(id)
#     bankers = Banker.query.options(joinedload(Banker.financial_agreements).joinedload(FinancialAgreement.tables_finance)).order_by(Banker.name).all()

#     image_fields = ['rg_cnh_completo', 'contracheque', 'rg_frente', 'rg_verso', 'extrato_consignacoes', 'comprovante_residencia', 'selfie', 'comprovante_bancario', 'detalhamento_inss', 'historico_consignacoes_inss']

#     if isinstance(proposal.created_at, str):
#         proposal.created_at = datetime.strptime(proposal.created_at, "%Y-%m-%d %H:%M:%S")

#     image_paths = UploadProposal(proposal_id=proposal.id, creator_id=proposal.creator_id, image_fields=image_fields, created_at=proposal.created_at).list_images()


#     if request.method == 'POST':
#         proposal.active = 'active' in request.form
#         proposal.number_proposal = request.form.get("number_proposal")
                
#         identifier = f"number_contrato_{proposal.id}_digitador_{proposal.creator_id}"

#         base_path = os.path.join('proposta', proposal.created_at.strftime('%Y'), proposal.created_at.strftime('%m'), proposal.created_at.strftime('%d'), identifier)

#         for field in image_fields:
#             field_files = request.files.getlist(field)
#             if field_files:
#                 field_base_path = os.path.join(base_path, field)
#                 image_paths = UploadProposal().save_images(field_files, field_base_path)
#                 setattr(proposal, field, ','.join(image_paths))
        
#         proposal.aguardando_digitacao = 'aguardando_digitacao' in request.form
#         proposal.pendente_digitacao = 'pendente_digitacao' in request.form
#         proposal.contrato_digitacao =  'contrato_digitacao' in request.form
#         proposal.aguardando_aceite_do_cliente = 'aguardando_aceite_do_cliente' in request.form
#         proposal.aguardando_aceite_do_cliente = 'aguardando_aceite_do_cliente' in request.form
#         proposal.aceite_feito_analise_do_banco = 'aceite_feito_analise_do_banco' in request.form
#         proposal.contrato_pendente_pelo_banco = 'contrato_pendente_pelo_banco' in request.form
#         proposal.aguardando_pagamento = 'aguardando_pagamento' in request.form
#         proposal.contratopago = 'contratopago' in request.form
#         proposal.completed_at = datetime.now()
#         proposal.completed_by = f"""Digitado por: {current_user.username}"""
#         db.session.commit()

#         flash('Proposta atualizada com sucesso!', 'success')
#         return redirect(url_for('operational.manage_state_contract'))
        
#     return render_template("operational/details_contract.html", proposal=proposal, bankers=bankers, image_paths=image_paths)


# @bp_operational.route('/operational/remove-image/<int:proposal_id>', methods=['POST'])
# @login_required
# def remove_image(proposal_id):
#     data = request.get_json()
#     field = data.get('field')
#     path = data.get('path')

#     full_path = os.path.join(os.getcwd(), 'proposta', path)
#     if os.path.exists(full_path):
#         os.remove(full_path)
#         return jsonify({'success': True})
#     else:
#         return jsonify({'success': False, 'message': 'Imagem não encontrada.'}), 404