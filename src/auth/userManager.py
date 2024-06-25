from flask import Blueprint, request, render_template, redirect, url_for, flash
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from flask import session
from ..models.user import User

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

    return render_template("login.html", user=current_user)


@bp_auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Você foi deslogado com sucesso.', category='success')
    return redirect(url_for("auth.login"))
