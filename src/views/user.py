import sys

from flask import Blueprint, render_template
from flask import url_for, jsonify
from flask import redirect, request, flash
from flask_login import login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from ..models.user import User
from ..external import db 

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


@bp_user.route("/promoters")
def promoters():
    """List promoters and sellers"""
    users = User.query.order_by(User.user_identification).all()
    return render_template("partials/promoters_partial.html", users=users)


@bp_user.route("/registerpromoters", methods=['POST'])
def post_promoters():
    """Add promoters"""
    try:
        username = request.form['username'].strip()
        user_identification = request.form['user_identification'].strip()
        type_user = request.form['type_user'].strip()
        password = request.form['password'].strip()

        if not (username and user_identification and type_user and password):
            return jsonify({'error': 'Todos os campos são obrigatórios'}), 400

        password_hash = generate_password_hash(password)

        new_user = User(
            user_identification=user_identification, 
            username=username, 
            password=password_hash, 
            type_user=type_user
        )
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'Cadastro realizado com sucesso!'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao registrar promotor: {e}", file=sys.stderr)  # Log no servidor
        return jsonify({'error': 'Erro interno do servidor'}), 500


@bp_user.route("/get-user")
def get_register_form():
    """Route partialas register promoters and users"""
    return render_template("partials/register_promoters.html")



@bp_user.route("/editpromoters/<int:id>", methods=['POST', 'PUT'])  # Permitir POST e PUT
def edit_promoters(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.user_identification = request.form['user_identification']
        user.type_user = request.form['type_user']
        user.password = generate_password_hash(request.form['password']) 
        db.session.commit()
        return redirect(url_for('some_view_function'))
    
    
@bp_user.route("/deletepromoters/<int:id>", methods=['POST'])
def delete_promoters(id):
    """Delete promoters and users"""
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('promoters'))