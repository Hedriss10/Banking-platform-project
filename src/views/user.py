import sys
from flask_sqlalchemy import pagination
from flask import Blueprint, render_template
from flask import url_for, jsonify, abort
from flask import redirect, request, flash
from flask_login import login_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from src import db 

from ..utils.generator_password import generator_password

from ..models.user import User

bp_user = Blueprint("users", __name__)


@bp_user.route("/promoters")
@login_required
def promoters():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    try:
        pagination = User.query.order_by(User.user_identification).paginate(page=page, per_page=per_page, error_out=True)
        users = pagination.items
        return render_template("partials/promoters_partial.html", users=users, pagination=pagination)
    except Exception as e:
        print(f"Erro ao recuperar os dados: {e}")
        abort(404)


@bp_user.route("/registerpromoters", methods=['POST'])
@login_required
def post_promoters():
    """Add promoters"""
    try:
        username = request.form['username'].strip()
        lastname = request.form['lastname'].strip()
        email = request.form['email'].strip()
        user_identification = request.form['user_identification'].strip()
        type_user = request.form['type_user']
        
        if not (username and user_identification and type_user):
            return jsonify({'error': 'Todos os campos são obrigatórios'}), 400        
        
        new_user = User(
            user_identification=user_identification, # cpf
            username=username, # name
            lastname=lastname, # sobrenome
            email=email, 
            password=generator_password(size=8), 
            type_user_func=type_user # cargo do usuário
        )
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'Cadastro realizado com sucesso!'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao registrar promotor: {e}", file=sys.stderr)  # Log no servidor
        return jsonify({'message': 'Não pode cadastrar dois o mais usuários com o mesmo nome'}), 500


@bp_user.route("/get-user")
@login_required
def get_register_form():
    """Route partialas register promoters and users"""
    return render_template("partials/register_promoters.html")


@bp_user.route("/edit-promoters", methods=['GET'])
@login_required
def get_edit_form():
    """Route partials edit promoters and users"""
    users = User.query.order_by(User.user_identification).all()
    return render_template("partials/edit_promoters.html", users=users)


@bp_user.route("/delete-promoters", methods=['GET'])
@login_required
def get_delete_form():
    """Route partials delete promoters and users"""
    users = User.query.order_by(User.user_identification).all()
    return render_template("partials/delete_promoters.html", users=users)


@bp_user.route("/update-promoter/<int:id>", methods=['POST'])
@login_required
def update_promoter(id):
    """Route edit user"""
    user = User.query.get_or_404(id)
    data = request.get_json()
    
    user.username = data.get('username', user.username)
    user.user_identification = data.get('user_identification', user.user_identification)
    user.type_user = data.get('type_user', user.type_user)

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Usuário atualizado com sucesso!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp_user.route("/searchpromoters")
@login_required
def search_promoters():
    query = request.args.get('query', '')
    users = User.query.filter(User.username.ilike(f'%{query}%')).all()
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'user_identification': user.user_identification,
        'type_user': user.type_user
    } for user in users]), 200



@bp_user.route("/deletepromoters/<int:id>", methods=['POST'])
@login_required
def delete_promoters(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Usuário deletado com sucesso!'}), 200
