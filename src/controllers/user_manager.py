import uuid
from src import db
from flask import session
from flask_login import logout_user, login_user
from werkzeug.security import check_password_hash, generate_password_hash
from src.models.bsmodels import User


class UsermanageControllers:
    
    def __init__(self, current_user):
        self.current_user = current_user
        
    def reset_password(self, user_id, new_password):
        try:
            user = User.query.filter_by(user_identification=user_id).first()

            if not user:
                return {'error': 'Usuário não encontrado', 'status': 404}
            user.password = generate_password_hash(new_password)
            db.session.commit()
            return {'success': True, 'message': 'Senha atualizada com sucesso!'}
        
        except Exception as e:
            db.session.rollback()
            return {'error': str(e), 'status': 500}
        
        
    def login_controllers(self, user_id, password):
        user = User.query.filter_by(user_identification=user_id).first()

        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                session['type_user_func'] = user.type_user_func
                session_token = str(uuid.uuid4())
                user.session_token = session_token
                db.session.commit()
                return {'success': True}
            else:
                return {'error': 'Sua senha está incorreta.'}
        else:
            return {'error': 'Usuário não está cadastrado.'}