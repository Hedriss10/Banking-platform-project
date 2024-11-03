from flask import (Blueprint, render_template, url_for, jsonify, redirect, request,  flash)
from flask_login import login_required, current_user 
from src import db

from src.controllers.operational import OperationalControllers

bp_operational = Blueprint("operational", __name__)

@bp_operational.route("/list-operational-contract")
@login_required
def manage_list_contract():    
    return render_template("operational/manage_list.html")

@bp_operational.route("/manage-operational")
@login_required
def manage_operational():
    """
        list board status proposal_
    Returns:
        _type_: return list board proposal
    """
    data = OperationalControllers(current_user=current_user).manage_operational_controllers(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template("operational/manage_operational.html", **data)

@bp_operational.route("/state-contract")
@login_required
def manage_state_contract():
    """
        Function to list the type of contract and control administrative operations
    Returns:
        _type_: list tables
    """
    proposal_data, tables_paginated = OperationalControllers(current_user=current_user).manage_state_contract_controllers(page=request.args.get('page', 1, type=int), per_page=10, search_term=request.args.get('search', '').lower())
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(proposal_data)
    
    return render_template("operational/state_contract.html", proposal=proposal_data, pagination=tables_paginated)

@bp_operational.route('/operational/available-contracts-count', methods=['GET'])
@login_required
def available_contracts_count():
    return jsonify({'available_contracts': OperationalControllers(current_user=current_user).available_contract_count_controllers()})

@bp_operational.route("/operational/edit-proposal/<int:id>", methods=['GET', 'POST'])
@login_required
def manage_edit_contract(id):
    """
        Edit proposal contract.
    Renders the form with current proposal data, bankers, and encoded images.
    """
    bankers, proposal, image_paths = OperationalControllers(current_user=current_user).manage_edit_contract_controllers(proposal_id=id, request=request)

    return render_template("operational/edit_contract.html", bankers=bankers, proposal=proposal, image_paths=image_paths)

@bp_operational.route('/operational/delete-proposal/<int:id>', methods=['POST'])
@login_required
def manage_delete_contract(id):
    """
    Endpoint to delete a proposal contract by ID.
    """
    response = OperationalControllers(current_user=current_user).manage_delete_contract_controllers(id=id)
    
    if response['success']:
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False, 'error': response['error']}), 500

@bp_operational.route('/operational/details/<int:id>', methods=['GET', 'POST'])
@login_required
def manage_details_contract(id):
    """
    View and edit details of a proposal contract.
    """
    # Use controller to handle logic and data retrieval
    success, bankers, proposal = OperationalControllers(current_user=current_user).manage_details_contract_controllers(id=id, request=request)

    if success:
        flash('Proposta atualizada com sucesso!', 'success')
        return redirect(url_for('operational.manage_state_contract'))

    return render_template("operational/details_contract.html", proposal=proposal, bankers=bankers)

@bp_operational.route('/operational/remove-image/<int:proposal_id>', methods=['POST'])
@login_required
def remove_image(proposal_id):
    data = request.get_json()
    field = data.get('field')
    
    result = OperationalControllers(current_user=current_user.id).remove_image_controllers(proposal_id, field)

    if result:
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Erro ao atualizar o banco de dados.'}), 500