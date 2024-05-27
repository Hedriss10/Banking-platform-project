from flask import Blueprint, render_template
from flask import url_for
from flask import redirect, request, flash
from flask_login import login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from ..models.user import User


bp_user = Blueprint("users", __name__)

@bp_user.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user']
        password = request.form['password']
       
        user = User.query.filter_by(user_identification=int(user_id)).first()
        if user:
            print("Senha do banco",type(user.password))
            print("Senha do request",type(password))
            if check_password_hash(user.password, password):
                flash("Logado com sucesso!", category='success')
                login_user(user, remember=True)
                return redirect(url_for('overview.home'))
            else:
                flash('Sua senha está incorreta.', category='error')
        else:
            flash('Usuário não está cadastrado.', category='error')

    return render_template("login.html", user=current_user)


@bp_user.route("/get-users")
def users():
    return render_template("register_account.html")
