from flask import (Blueprint, request, render_template, redirect, url_for, flash, jsonify)
from flask_login import  logout_user, login_required, current_user
from src.controllers.user_manager import UsermanageControllers


bp_auth = Blueprint("auth", __name__, template_folder="templates")

@bp_auth.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user')
        password = request.form.get('password')

        response = UsermanageControllers(current_user=current_user).login_controllers(user_id, password)
        
        if isinstance(response, dict) and 'error' in response:
            flash(response['error'], category='error')
        else:
            return redirect(url_for('overview.home'))
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
def reset_password():
    """Route for reset password"""
    user_id = request.form.get('userId')
    new_password = request.form.get('newPassword')
    
    if not user_id:
        return jsonify({'error': 'CPF não fornecido'}), 400
    
    if not new_password:
        return jsonify({'error': 'Senha não fornecida'}), 400

    response = UsermanageControllers(current_user=current_user).reset_password(user_id, new_password)

    if isinstance(response, dict) and 'error' in response:
        return jsonify(response), response.get('status', 500)
    
    return jsonify({'success': True, 'message': 'Senha atualizada com sucesso!'}), 200
