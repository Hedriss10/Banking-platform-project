from werkzeug.security import generate_password_hash
from src.models.bsmodels import User
from src import db 

class UserControllers:
    
    def __init__(self, current_user):
        self.current_user = current_user
         
    def users_controllers(self, page, per_page, search_term):
        
        query = User.query
        
        if search_term:
            query = query.filter(
            User.username.ilike(f'%{search_term}%') |
            User.lastname.ilike(f'%{search_term}%') |
            User.email.ilike(f'%{search_term}%') | 
            User.user_identification.ilike(f'%{search_term}%') | 
            User.type_user_func.ilike(f'%{search_term}%') 
        )
        
        tables_paginated = query.order_by(User.username.desc()).paginate(page=page, per_page=per_page)
        
        user_data = [{
            'username': user.username,
            'lastname': user.lastname,
            'type_user_func': user.type_user_func,
            'email': user.email,
            'user_identification': user.user_identification,
        } for user in tables_paginated.items]
        
        return tables_paginated, user_data

    def update_permissions_controller(self, user_id, new_type_user_func, current_user_type):

        try:
            if current_user_type != "Administrador":
                return {'message': 'Você não tem permissão para alterar as permissões de usuário.'}, 403

            user = User.query.get_or_404(user_id)
            user.type_user_func = new_type_user_func
            db.session.commit()
        
            return {'success': True, 'message': 'Permissão atualizada com sucesso!'}, 200
        
        except Exception:
            db.session.rollback()
            return {'message': 'Erro ao atualizar a permissão do usuário.'}, 500
    
    def permissions_controllers(self, page, per_page, search_term):
        query = User.query
        
        if search_term:
            query = query.filter(
                User.username.ilike(f'%{search_term}%') |
                User.lastname.ilike(f'%{search_term}%') |
                User.email.ilike(f'%{search_term}%') | 
                User.user_identification.ilike(f'%{search_term}%') | 
                User.type_user_func.ilike(f'%{search_term}%') 
            )
            
        tables_paginated = query.order_by(User.username.desc()).paginate(page=page, per_page=per_page)
    
        user_data = [{
            'username': user.username,
            'lastname': user.lastname,
            'type_user_func': user.type_user_func,
            'email': user.email,
            'user_identification': user.user_identification,
        } for user in tables_paginated.items]
        
        return tables_paginated, user_data
                
    def add_users_controller(self, data):
        try:
            # Extração e validação dos campos
            required_fields = ['username', 'lastname', 'email', 'password', 'user_identification', 'type_user_func', 'type_contract']
            missing_fields = [field for field in required_fields if not data.get(field)]

            if missing_fields:
                return {'error': f'Campos obrigatórios ausentes: {", ".join(missing_fields)}'}, 400

            # Criação do usuário
            new_user = User(
                user_identification=data['user_identification'].strip(),
                username=data['username'].strip(),
                lastname=data['lastname'].strip(),
                email=data['email'].strip(),
                password=data['password'],
                type_user_func=data['type_user_func'],
                typecontract=data['type_contract']
            )

            # Salvando o usuário no banco
            db.session.add(new_user)
            db.session.commit()
            return {'message': 'Usuário cadastrado com sucesso'}, 201

        except Exception as e:
            db.session.rollback()
            return {'error': 'Não foi possível cadastrar o usuário, verifique se o e-mail ou CPF já existem'}, 500

    def update_promoter_controller(self, user_id, new_password):
        try:
            if not new_password:
                return {'error': 'Senha não fornecida'}, 400

            user = User.query.get_or_404(user_id)
            user.password = generate_password_hash(new_password)
            
            db.session.commit()
            return {'success': True, 'message': 'Senha atualizada com sucesso!'}, 200

        except Exception as e:
            db.session.rollback()
            return {'error': 'Erro ao atualizar a senha: ' + str(e)}, 500
        
    def update_promoter_block_controller(self, user_id):
        
        try:
            user = User.query.get_or_404(user_id)            
            user.is_block = True
            user.is_inactive = True
            db.session.commit()
            return {'success': True, 'message': 'Usuário bloqueado com sucesso!'}, 200

        except Exception as e:
            db.session.rollback()
            return {'error': True, 'message': f'Erro ao bloquear o usuário: {str(e)}'}, 500
        
    def update_promoter_active_user_controller(self, user_id):
        
        try:
            user = User.query.get_or_404(user_id)
            user.is_block = False
            user.is_inactive = False
            db.session.commit()
            return {'success': True, 'message': 'Usuário desbloqueado com sucesso!'}, 200

        except Exception as e:
            db.session.rollback()
            return {'error': True, 'message': f'Erro ao desbloquear o usuário: {str(e)}'}, 500
        
    def search_promoters_controller(self, search_query):
        try:
            users = User.query.filter(User.username.ilike(f'%{search_query}%')).all()
            user_data = [{
                'username': user.username,
                'type_user_func': user.type_user_func,
            } for user in users]

            return {'data': user_data}, 200

        except Exception as e:
            return {'error': True, 'message': f'Erro ao buscar promotores: {str(e)}'}, 500
        
    def delete_promoters_controller(self, user_id):
        try:
            user = User.query.get_or_404(user_id)
            db.session.delete(user)
            db.session.commit()
            
            return {'success': True, 'message': 'Usuário deletado com sucesso!'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': True, 'message': f'Erro ao deletar o usuário: {str(e)}'}, 500