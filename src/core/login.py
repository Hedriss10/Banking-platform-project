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

            if not data.get("cpfLogin") and not data.get("passwordLogin"):
                return jsonify({"error": "cpf_is_required_and_password"}), 400

            user = User.query.filter_by(cpf=data.get("cpfLogin"), is_deleted=False).first()
            if not user:
                return jsonify({"error": "user_not_found"}), 404

            if not check_password_hash(user.password, data.get("passwordLogin")):
                return jsonify({"error": "invalid_password"}), 400

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
            return jsonify({'success': True, 'message': 'login_successfully', 'redirect_url' : '/home'}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500


    def reset_password(self, data: dict):
        try:
            if not data.get("userId") and not data.get("newPassword"):
                return jsonify({'error': 'cpf_is_required_and_password'}), 400
            
            user = User.query.filter_by(cpf=data.get("userId")).first()

            if not user:
                return jsonify({'error': 'user_not_found'}), 404

            if user:
                user.password = generate_password_hash(data.get("newPassword"))
                user.updated_at = datetime.now()
                db.session.add(user)
                db.session.commit()

            return jsonify({'success': True, 'message': 'update_password_sucessfully', 'redirect_url' : '/login'}), 200
        
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500