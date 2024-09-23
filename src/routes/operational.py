import os

from flask_sqlalchemy import pagination
from flask import (Blueprint, render_template, url_for, jsonify, abort, redirect, request, current_app, flash, send_from_directory)
from flask_login import login_required, current_user 
from src import db
from src.models.bsmodels import UserProposal
from src.utils.proposal import UploadProposal
from datetime import datetime


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
    """
        Function for listing all proposals in the table
    """
    
    query = UserProposal.query
    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search_term = request.args.get('search', '').lower()
    
    try:
        search_rate = float(search_term)
    except ValueError:
        search_rate = None

    if search_term:
        query = query.filter(
            UserProposal.name_and_lastname.ilike(f'%{search_term}%') |  # Filtra pelo nome do contrato
            UserProposal.created_at.ilike(f'%{search_term}%') |  # Filtra pela data de criação
            UserProposal.cpf.ilike(f'%{search_term}%')  # Filtra pelo CPF do contrato
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
        'edit_at': p.edit_at if p.edit_at else "Não foi editado ainda",
        'completed_at': p.completed_at if p.completed_at else "Não foi digitado ainda"
    } for p in tables_paginated.items]

    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(proposal_data)
    
    return render_template("operational/state_contract.html", proposal=proposal_data, pagination=tables_paginated)


@bp_operational.route('/operational/available-contracts-count', methods=['GET'])
@login_required
def available_contracts_count():
    available_count = UserProposal.query.filter_by(active=0, block=0, is_status=0, progress_check=0).count()
        
    return jsonify({'available_contracts': available_count})


@bp_operational.route("/operational/edit-proposal/<int:id>", methods=['GET', 'POST'])
@login_required
def manage_edit_contract(id):
    """
        Editar proposta
    """
    proposal = UserProposal.query.get_or_404(id)

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
        
        proposal.active = 'active' in request.form
        proposal.block = 'block' in request.form
        proposal.is_status = 'is_status' in request.form
        proposal.progress_check = 'progress_check' in request.form 

        identifier = f"number_contrato_{proposal.id}_digitador_{proposal.creator_id}"

        base_path = os.path.join('proposta', proposal.created_at.strftime('%Y'), proposal.created_at.strftime('%m'), proposal.created_at.strftime('%d'), identifier)

        for field in image_fields:
            field_files = request.files.getlist(field)
            if field_files:
                field_base_path = os.path.join(base_path, field)
                image_paths = UploadProposal().save_images(field_files, field_base_path)
                setattr(proposal, field, ','.join(image_paths))
        
        proposal.edit_at = datetime.now()
        db.session.commit()

        flash('Proposta atualizada com sucesso!', 'success')
        return redirect(url_for('operational.manage_state_contract'))

    return render_template("operational/edit_contract.html", proposal=proposal, image_paths=image_paths)


@bp_operational.route('/uploads/<path:filename>')
@login_required
def serve_image(filename):
    """
        Função para servir as imagens do servidor.
    """
    base_dir = os.path.join(os.getcwd(), 'proposta')

    full_path = os.path.join(base_dir, filename)

    if not os.path.exists(full_path):
        print(f"Caminho não encontrado: {full_path}")
        return abort(404)

    if not os.path.isfile(full_path):
        print(f"O caminho não é um arquivo: {full_path}")
        return abort(404)

    try:
        return send_from_directory(base_dir, filename)
    except Exception as e:
        print(f"Erro ao servir a imagem: {e}")
        return abort(500)


@bp_operational.route('/operational/delete-proposal/<int:id>', methods=['POST'])
@login_required
def manage_delete_contract(id):
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


@bp_operational.route('/operational/details/<int:id>', methods=['GET', 'POST'])
@login_required
def manage_details_contract(id):
    """
        Editar proposta
    """
    proposal = UserProposal.query.get_or_404(id)

    image_fields = ['rg_cnh_completo', 'contracheque', 'rg_frente', 'rg_verso', 'extrato_consignacoes', 'comprovante_residencia', 'selfie', 'comprovante_bancario', 'detalhamento_inss', 'historico_consignacoes_inss']

    if isinstance(proposal.created_at, str):
        proposal.created_at = datetime.strptime(proposal.created_at, "%Y-%m-%d %H:%M:%S")

    image_paths = UploadProposal(proposal_id=proposal.id, creator_id=proposal.creator_id, image_fields=image_fields, created_at=proposal.created_at).list_images()

 
    if request.method == 'POST':
        proposal.active = 'active' in request.form
        identifier = f"number_contrato_{proposal.id}_digitador_{proposal.creator_id}"

        base_path = os.path.join('proposta', proposal.created_at.strftime('%Y'), proposal.created_at.strftime('%m'), proposal.created_at.strftime('%d'), identifier)

        for field in image_fields:
            field_files = request.files.getlist(field)
            if field_files:
                field_base_path = os.path.join(base_path, field)
                image_paths = UploadProposal().save_images(field_files, field_base_path)
                setattr(proposal, field, ','.join(image_paths))
        
        proposal.block = 0
        proposal.is_status = 0
        proposal.progress_check = 0
        proposal.completed_at = datetime.now()
        db.session.commit()

        flash('Proposta atualizada com sucesso!', 'success')
        return redirect(url_for('operational.manage_state_contract'))
        
    return render_template("operational/details_contract.html", proposal=proposal, image_paths=image_paths)