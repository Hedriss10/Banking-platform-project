from flask import (Blueprint, render_template, url_for, jsonify, redirect, request)
from flask_login import login_required, current_user
from src.controllers.user import UserControllers

bp_user = Blueprint("users", __name__)

@bp_user.route("/user")
@login_required
def users():
    """ User`s
            Function for list users
    Returns:
        _list_: return [list]
    """
    tables_paginated, user_data = UserControllers(current_user=current_user).users_controllers(page=request.args.get('page', 1, type=int), per_page=10, search_term=request.args.get('search', '').lower())

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(user_data)
    
    return render_template("user/user_manager.html", users=tables_paginated.items, pagination=tables_paginated)

@bp_user.route("/users-permissinon")
@login_required
def permission_users():
    """ Type Permissions user
        list users 
    Returns:
        _return_: _[permissions users]_
    """

    tables_paginated, user_data = UserControllers(current_user=current_user).permissions_controllers(page=request.args.get('page', 1, type=int), per_page=10, search_term=request.args.get('search', '').lower()) 

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(user_data)
    
    return render_template("user/user_manage_permission.html", users=tables_paginated, pagination=tables_paginated)

@bp_user.route("/alter-permission/<int:id>", methods=['POST'])
@login_required
def update_permission(id):
    """
        Update permissions filter by id users, alter permissions
    Args:
        id (_type_): users

    Returns:
        _type_: Update filter by id
    """

    new_type_user_func = request.json.get('type_user_func')
    current_user_type = current_user.type_user_func

    response, status_code = UserControllers(current_user=current_user).update_permissions_controller(id, new_type_user_func, current_user_type)
    return jsonify(response), status_code

@bp_user.route("/registerpromoters", methods=['POST'])
@login_required
def add_users():
    """Adiciona promotores e usuários"""
    data = request.form.to_dict()
    
    response, status_code = UserControllers(current_user=current_user).add_users_controller(data)
    
    if status_code == 201:
        return redirect(url_for("overview.home"))
    else:
        return jsonify(response), status_code

@bp_user.route("/update-promoter/<int:id>", methods=['POST'])
@login_required
def update_promoter(id):
    """ 
        Update password of promoter

    Args:
        id (_type_): id

    Returns:
        _type_: New Password of promoter filter by id
    """
    
    data = request.get_json()
    new_password = data.get('password')
    
    response, status_code = UserControllers(current_user=current_user).update_promoter_controller(id, new_password)
    return jsonify(response), status_code

@bp_user.route("/update-promoter/block/<int:id>", methods=['POST'])
@login_required
def update_promoter_block(id):
    """
        Update promoter block
    Args:
        id (_type_): Alter flag user for block
    Returns:
        _type_: Return block users
    """
    
    response, status_code = UserControllers(current_user=current_user).update_promoter_block_controller(id)
    return jsonify(response), status_code

@bp_user.route("/update-promoter/active/<int:id>", methods=['POST'])
@login_required
def update_promoter_active_user(id):
    """
        Update promoter active user
    Args:
        id (_type_): id
    Returns:
        _type_: return filter by id
    """    
    response, status_code = UserControllers(current_user=current_user).update_promoter_active_user_controller(id)
    return jsonify(response), status_code

@bp_user.route("/searchpromoters")
@login_required
def search_promoters():
    """Route to search promoters by username"""
    query = request.args.get('query', '')
    
    response, status_code = UserControllers(current_user=current_user).search_promoters_controller(query)
    return jsonify(response), status_code

@bp_user.route("/deletepromoters/<int:id>", methods=['POST'])
@login_required
def delete_promoters(id):   
    """Route to delete a promoter"""
    
    response, status_code = UserControllers(current_user=current_user).delete_promoters_controller(id)
    return jsonify(response), status_code