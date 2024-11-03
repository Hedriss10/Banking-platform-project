import os 
import base64
import json

from datetime import datetime
from flask import (Blueprint, render_template, url_for, jsonify, abort, redirect, request, current_app, flash, send_from_directory)
from flask_login import login_required, current_user 
from src import db
from sqlalchemy.orm import joinedload
from src.utils.proposal import UploadProposal
from src.models.bsmodels import User, Banker, FinancialAgreement, TablesFinance, Proposal

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from src.token.generate_token import load_private_key, get_public_key_str


from src.controllers.proposal import ProposalControllers


# derocators api module
bp_proposal = Blueprint("proposal", __name__)


@bp_proposal.route("/proposal")
@login_required
def manage_proposal():
    """Function para rank de comissão associando a tabela Flat da coluna TablesFinance"""    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search_term = request.args.get('search', '').lower()

    try:
        search_rate = float(search_term)
    except ValueError:
        search_rate = None

    banks_data ,bankers, tables_paginated = ProposalControllers(current_user=current_user).state_tables_finance_controllers(search_term=search_term, page=page, per_page=per_page)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(banks_data)
    return render_template("proposal/manage_proposal.html", bankers=bankers ,banks=banks_data, pagination=tables_paginated)

@bp_proposal.route("/creat-proposal", methods=['GET'])
@login_required
def creat_proposal():
    """Function to create a proposal."""
    bankers = ProposalControllers(current_user=current_user).page_create_proposal_controllers()
    public_key_str = get_public_key_str()
    return render_template("proposal/creat_proposal.html", bankers=bankers, public_key=public_key_str)

@bp_proposal.route("/search-tables", methods=['GET'])
@login_required
def search_tables():
    """Function for search tables"""
    search_term = request.args.get('query', '')
    return ProposalControllers(current_user=current_user).filter_tables_with_search(search_term=search_term)

@bp_proposal.route("/proposal-status")
@login_required
def state_proposal():
    """ State Proposal
        Function to return the entire list of user proposals filtered by the unique key
    Returns:
        _type_: args 
        return list proposal filter by id 
    """
    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search_term = request.args.get('search', '').lower()

    proposal_data, tables_paginated = ProposalControllers(current_user=current_user.id).state_proposal_controllers(search_term=search_term, page=page, per_page=per_page)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(proposal_data)
    
    return render_template("proposal/state_proposal.html", proposal=proposal_data, pagination=tables_paginated)

@bp_proposal.route("/proposal/new-proposal", methods=['POST'])
@login_required
def add_proposal():
    """Function for register proposal"""
    encrypted_data = request.form.get('encrypted_data')
    encrypted_key = request.form.get('encrypted_key')
    iv_base64 = request.form.get('iv')

    if not encrypted_data or not encrypted_key or not iv_base64:
        return jsonify({'error': 'Dados criptografados faltando'}), 400

    try:
        aes_key = load_private_key().decrypt(
            base64.b64decode(encrypted_key),
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
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
        new_proposal = ProposalControllers(current_user=current_user).add_proposal_controllers(form_data=form_data, request=request)
        db.session.add(new_proposal)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Contrato registrado com sucesso'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Erro ao processar o formulário: %s", e)
        return jsonify({'error': str(e)}), 500

@bp_proposal.route("/proposal/edit-proposal/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_proposal(id):
    """ 
        Edit Proposal
        Function to edit the proposal, there is a business rule, where if the operational sector collects the proposal, there is no way to edit it anymore
    Args:
        id (_type_): id proposal

    Returns:
        _type_: bankers, proposal, image_paths
    """
    
    form_data = None
    print(request.form)
    if request.method == 'POST':
        form_data = request.form
        response = ProposalControllers(current_user=current_user).edit_proposal_controllers(id=id, request=request, form_data=form_data)
        return jsonify(response), 200 if response["success"] else 500

    response = ProposalControllers(current_user=current_user).edit_proposal_controllers(id=id, request=request, form_data=form_data)
        
    if response["success"]:
        return render_template("proposal/edit_proposal.html", bankers=response["bankers"], proposal=response["proposal"], image_paths=response["image_paths"])
    else:
        print(response["error"])
        return jsonify({"error": response["error"]}), 500
    

@bp_proposal.route('/proposal/<int:proposal_id>/<string:field>')
@login_required
def serve_image(proposal_id, field):
    """Serve a imagem binária armazenada no banco de dados como base64 para o campo especificado."""
    
    proposal = Proposal.query.filter_by(id=proposal_id).first()
    
    if not proposal or not hasattr(proposal, field):
        print(f"Proposta ou campo não encontrado para ID {proposal_id} e campo {field}")
        return abort(404)
    
    image_data = getattr(proposal, field)
    
    if not image_data:
        print(f"Imagem não encontrada para o campo {field}")
        return abort(404)
    
    try:
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        return jsonify({'image': image_base64})
    except Exception as e:
        print(f"Erro ao codificar a imagem: {e}")
        return abort(500)

@bp_proposal.route("/proposal/delete-proposal/<int:id>", methods=['GET', 'POST'])
@login_required
def delete_proposal(id):
    """Função para deletar uma proposta e remover todas as imagens associadas."""
    
    try:
        proposal = ProposalControllers(current_user=current_user).delete_proposal_controllers(id=id)
        db.session.delete(proposal)
        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao excluir a proposta: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp_proposal.route('/proposal/remove-image/<int:proposal_id>', methods=['POST'])
@login_required
def remove_image(proposal_id):
    data = request.get_json()
    field = data.get('field')
    
    result = ProposalControllers(current_user=current_user.id).remove_image_proposal_controllers(proposal_id, field)

    if result:
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Erro ao atualizar o banco de dados.'}), 500

