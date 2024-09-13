from flask_sqlalchemy import pagination
from flask import (Blueprint, render_template, url_for, jsonify, abort, redirect, request, current_app, flash, send_from_directory)
from flask_login import login_required, current_user 
from src import db
from src.models.bsmodels import UserProposal
from src.utils.proposal import UploadProposal
import os

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
        Function for list table all proposal
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
            UserProposal.name_and_lastname.ilike(f'%{search_term}%') |  # Filtrar pelo o nome da campanha
            UserProposal.created_at.ilike(f'%{search_term}%') |# Filtro pelo código da tabela
            UserProposal.cpf.ilike(f'%{search_term}') #  filtrando pelo o cpf do contrato
        )
    
    tables_paginated = query.order_by(UserProposal.created_at.desc()).paginate(page=page, per_page=per_page)

    proposal_data = [{
        'id': p.id,
        'creator_name': p.creator.username if p.creator else 'Desconhecido',
        'name_and_lastname': p.name_and_lastname,
        'created_at': p.created_at.strftime('%d/%m/%Y'),
        'cpf': p.cpf,
        'active': p.active,
        'block': p.block,
        'is_status': p.is_status
    } for p in tables_paginated.items]

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(proposal_data)
    
    return render_template("operational/state_contract.html", proposal=proposal_data, pagination=tables_paginated)



@bp_operational.route("/operational/edit-proposal/<int:id>", methods=['GET', 'POST'])
@login_required
def manage_edit_contract(id):
    """
        Edit contract
    """
    
    proposal = UserProposal.query.get_or_404(id)
    image_fields = [
        'rg_cnh_completo', 'contracheque', 'extrato_consignacoes',
        'comprovante_residencia', 'selfie', 'comprovante_bancario',
        'detalhamento_inss', 'historico_consignacoes_inss'
    ]

    creator_id = proposal.creator_id

    upload_proposal = UploadProposal()
    image_paths = upload_proposal.list_images(proposal_id=proposal.id, creator_id=creator_id, image_fields=image_fields)
    
    if request.method == 'POST':
        # Atualizar informações da proposta
        proposal.name_and_lastname = request.form.get('name_and_lastname')
        proposal.created_at = request.form.get('created_at') 
        proposal.active = 'active' in request.form
        proposal.block = 'block' in request.form
        proposal.is_status = 'is_status' in request.form
        
    return render_template("operational/edit_contract.html", proposal=proposal, image_paths=image_paths)


@bp_operational.route('/uploads/<path:filename>')
@login_required
def serve_image(filename):
    """
        Funcão para pegar as fotos do server.
    """
    base_dir = os.path.join(os.getcwd(), 'proposta')
    try:
        return send_from_directory(base_dir, filename)
    except FileNotFoundError:
        abort(404) 