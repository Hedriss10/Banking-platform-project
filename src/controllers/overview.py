

from src.models.bsmodels import User


class OverviewControllers:
    
    def __init__(self, current_user):
        self.current_user = current_user
        
        
    def get_user_profile(self, user_id):
        try:
            user = User.query.filter_by(user_identification=user_id).first()
            if not user:
                return {'error': True, 'message': 'Usuário não encontrado.'}, 404
            
            return user

        except Exception as e:
            return {'error': True, 'message': f'Erro ao buscar perfil do usuário: {str(e)}'}, 500
