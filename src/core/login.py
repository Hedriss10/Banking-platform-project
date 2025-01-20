from flask import jsonify
from flask_login import login_user
from werkzeug.security import check_password_hash
from src.auth.auth import UserAuth
from src.models.user import User
from src import db
from werkzeug.security import generate_password_hash
from datetime import datetime

class LoginCore:
    def __init__(self, user_id=None, *args, **kwargs):
        self.user_id = user_id

    def login_user(self, data: dict):
        try:
            cpf = data.get("cpfLogin")
            password = data.get("passwordLogin")

            if not cpf:
                return jsonify({"error": "cpf is required"}), 400
            if not password:
                return jsonify({"error": "Password is required"}), 400

            user = User.query.filter_by(cpf=cpf).where(User.is_deleted == False).first()
            if not user:
                return jsonify({"error": "User not found"}), 404

            if not check_password_hash(user.password, password):
                return jsonify({"error": "Invalid password"}), 400

            user_auth = UserAuth(
                id=user.id,
                username=user.username,
                email=user.email,
                password=user.password,
                role=user.role,
                session_token=user.session_token,
                is_active=user.is_acctive,
                is_block=user.is_block,
                is_deleted=user.is_deleted,
            )

            login_user(user_auth)
            return jsonify({"success": True}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500


    def reset_password(self, data: dict):
        try:
            user_id = data.get("userId")
            new_password = data.get("newPassword")
            
            if not user_id:
                return jsonify({'error': 'CPF não fornecido'}), 400
            
            if not new_password:
                return jsonify({'error': 'Senha não fornecida'}), 400
            
            user = User.query.filter_by(id=user_id).first()
            
            if not user:
                return jsonify({'error': 'Usuário não encontrado'}), 404
            
            user.password = generate_password_hash(new_password)
            user.updated_at = datetime.now()
            db.session.commit()
            return jsonify({'success': True, 'message': 'Senha atualizada com sucesso!'}), 200
        
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500