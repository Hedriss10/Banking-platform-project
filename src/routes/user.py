from flask_sqlalchemy import pagination
from flask import (Blueprint, render_template, url_for, jsonify, abort, redirect, request)
from flask_login import login_required, current_user
from src import db
from werkzeug.security import generate_password_hash
from src.models.bsmodels import User

bp_user = Blueprint("users", __name__)

@bp_user.route("/user")
@login_required
def users():
    """Get all users"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search_term = request.args.get('search', '').lower()
    query = User.query

    if search_term:
        query = query.filter(
            User.username.ilike(f'%{search_term}%') |
            User.lastname.ilike(f'%{search_term}%') |
            User.email.ilike(f'%{search_term}%') | 
            User.user_identification.ilike(f'%{search_term}%') | 
            User.type_user_func.ilike(f'%{search_term}%') 
        )
        
    tables_paginated = query.order_by(User.username.desc()).paginate(page=page, per_page=per_page)

    user_data = [{
        'username': user.username,
        'lastname': user.lastname,
        'type_user_func': user.type_user_func,
        'email': user.email,
        'user_identification': user.user_identification,
    } for user in tables_paginated.items]
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(user_data)
    
    return render_template("user/user_manager.html", users=tables_paginated.items, pagination=tables_paginated)


@bp_user.route("/users-permissinon")
@login_required
def permission_users():
    """"
        table permission users
    """
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search_term = request.args.get('search', '').lower()
    query = User.query

    if search_term:
        query = query.filter(
            User.username.ilike(f'%{search_term}%') |
            User.lastname.ilike(f'%{search_term}%') |
            User.email.ilike(f'%{search_term}%') | 
            User.user_identification.ilike(f'%{search_term}%') | 
            User.type_user_func.ilike(f'%{search_term}%') 
        )
        
    tables_paginated = query.order_by(User.username.desc()).paginate(page=page, per_page=per_page)
    
    user_data = [{
        'username': user.username,
        'lastname': user.lastname,
        'type_user_func': user.type_user_func,
        'email': user.email,
        'user_identification': user.user_identification,
    } for user in tables_paginated.items]
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(user_data)
    
    return render_template("user/user_manage_permission.html", users=tables_paginated, pagination=tables_paginated)


@bp_user.route("/alter-permission/<int:id>", methods=['POST'])
@login_required
def update_permission(id):
    """Alter permission of user to database"""
    
    user = User.query.get_or_404(id)
    new_type_user_func = request.json.get('type_user_func')
    try:
        if current_user.type_user_func == "Administrador":
            user.type_user_func = new_type_user_func
            db.session.commit()
            return jsonify({'success': True, 'message': 'Permissão atualizada com sucesso!'}), 200
        else:
            return jsonify({'message': 'Você não tem permissão para alterar as permissões de usuário.'}), 403

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erro ao atualizar a permissão do usuário.'}), 500



@bp_user.route("/registerpromoters", methods=['POST'])
@login_required
def add_users():
    """Add promoters and user"""
    try:
        username = request.form['username'].strip()
        lastname = request.form['lastname'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        user_identification = request.form['user_identification'].strip()
        type_user_func = request.form['type_user_func']
        typecontract = request.form['type_contract']
        
        
        if not (username and user_identification and password and type_user_func and type_user_func and typecontract):
            return jsonify({'error': 'Todos os campos são obrigatórios'}), 400
        
        new_user = User(
            user_identification=user_identification, # cpf
            username=username, # name
            lastname=lastname, # sobrenome
            email=email, # email,
            password=password, # senha 
            type_user_func=type_user_func, # cargo do usuário
            typecontract=typecontract, # tipo de funcuinário
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("overview.home"))

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Não pode cadastrar dois o mais usuários com o mesmo nome'}), 500


@bp_user.route("/update-promoter/<int:id>", methods=['POST'])
@login_required
def update_promoter(id):
    """Route edit password of user"""
    user = User.query.get_or_404(id)
    data = request.get_json()
    new_password = data.get('password')
    if new_password:
        user.password = generate_password_hash(new_password)
        try:
            db.session.commit()
            return jsonify({'success': True, 'message': 'Senha atualizada com sucesso!'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Senha não fornecida'}), 400


@bp_user.route("/update-promoter/block/<int:id>", methods=['POST'])
@login_required
def update_promoter_block(id):
    """Route to block and inactive in user"""
    user = User.query.get_or_404(id)
    user.is_block = True
    user.is_inactive = True
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Usuário bloqueado com sucesso!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': True, 'message': str(e)}), 500

@bp_user.route("/update-promoter/active/<int:id>", methods=['POST'])
@login_required
def update_prometer_ative_user(id):
    """Remove block and inactive user"""
    user = User.query.get_or_404(id)
    user.is_block = False
    user.is_inactive = False
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Usuário desbloqueado com sucesso!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': True, 'message': str(e)}), 500
     

@bp_user.route("/searchpromoters")
@login_required
def search_promoters():
    """search promoters """
    query = request.args.get('query', '')
    users = User.query.filter(User.username.ilike(f'%{query}%')).all()
    return jsonify([{
        'username': user.name,
        'type_user_func': user.type_user_func,
    } for user in users]), 200


@bp_user.route("/deletepromoters/<int:id>", methods=['POST'])
@login_required
def delete_promoters(id):
    """delete promoters"""
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Usuário deletado com sucesso!'}), 200
