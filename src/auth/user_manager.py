from flask import (Blueprint, request, render_template, redirect, url_for, flash, jsonify, session)
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from src.models.user import User
from src import db



bp_auth = Blueprint("auth", __name__)

@bp_auth.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user']
        password = request.form['password']
        user = User.query.filter_by(user_identification=user_id).first()
        
        if user:
            if check_password_hash(user.password, password):
                flash("Usuário logado com sucesso!", category='success')
                login_user(user, remember=True)
                session['type_user_func'] = user.type_user_func
                return redirect(url_for('overview.home'))
            else:
                flash('Sua senha está incorreta.', category='error')
        else:
            flash('Usuário não está cadastrado.', category='error')

    return render_template("login/login.html", user=current_user)


@bp_auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Você foi deslogado com sucesso.', category='success')
    return redirect(url_for("auth.login"))



@bp_auth.route("/reset-password", methods=['GET'])
def update_user():
    return render_template("login/pages-reset.html")


@bp_auth.route("/update-user", methods=['POST'])
# @login_required
def reset_password():
    """Route for reset password"""
    try:
        user_id = request.form['userId']
        new_password = request.form['newPassword']
                
        if not user_id:
            return jsonify({'error': 'CPF não fornecido'}), 400
        
        if not new_password:
            return jsonify({'error': 'Senha não fornecida'}), 400
    
        
        user = User.query.filter_by(user_identification=user_id).first()
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        user.password = generate_password_hash(new_password)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Senha atualizada com sucesso!'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
