from flask import Blueprint, request, render_template, redirect, url_for, flash
from src.core.login import LoginCore

bp_auth = Blueprint("auth", __name__, template_folder="templates")

@bp_auth.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data_dict = request.form.to_dict(flat=True)        
        user = LoginCore().get_login(data=data_dict)
        
        if user:
            return redirect(url_for("overview.home"))

        return redirect(url_for("auth.login"))

    return render_template("login/login.html")


@bp_auth.route("/logout")
def logout():
    flash('Você foi deslogado com sucesso.', category='success')
    return redirect(url_for("auth.login"))



@bp_auth.route("/reset-password", methods=['GET'])
def update_user():
    return render_template("login/pages-reset.html")


# @bp_auth.route("/update-user", methods=['POST'])
# # 
# def reset_password():
#     """Route for reset password"""
#     try:
#         user_id = request.form['userId']
#         new_password = request.form['newPassword']
                
#         if not user_id:
#             return jsonify({'error': 'CPF não fornecido'}), 400
        
#         if not new_password:
#             return jsonify({'error': 'Senha não fornecida'}), 400
    
        
#         user = User.query.filter_by(user_identification=user_id).first()
        
#         if not user:
#             return jsonify({'error': 'Usuário não encontrado'}), 404
        
#         user.password = generate_password_hash(new_password)
#         db.session.commit()
        
#         return jsonify({'success': True, 'message': 'Senha atualizada com sucesso!'}), 200
    
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500
