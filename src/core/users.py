from flask import jsonify
from flask_login import login_user
from werkzeug.security import check_password_hash
from src.models.user import User
from src import db
from werkzeug.security import generate_password_hash
from datetime import datetime

class UserCore:
    
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id

    def list_users(self, data: dict):
        try:
            page = int(data.get('page', 1))
            per_page = int(data.get('rows_per_page', 10))
            search_term = data.get('search', '').lower()
            query = User.query

            if search_term:
                query = query.filter(
                    User.username.ilike(f'%{search_term}%') |
                    User.lastname.ilike(f'%{search_term}%') |
                    User.email.ilike(f'%{search_term}%') |
                    User.role.ilike(f'%{search_term}%') |
                    User.cpf.ilike(f'%{search_term}%')
                )


            tables_paginated = query.order_by(User.username.desc()).paginate(page=page, per_page=per_page)

            user_data = [{
                'id': user.id,
                'username': user.username,
                'lastname': user.lastname,
                'role': user.role,
                'email': user.email,
                'cpf': user.cpf,
            } for user in tables_paginated.items]

            pagination = {
                'page': tables_paginated.page,
                'total_pages': tables_paginated.pages,
                'total_items': tables_paginated.total,
                'has_prev': tables_paginated.has_prev,
                'has_next': tables_paginated.has_next,
            }
            return jsonify({'users': user_data, 'pagination': pagination}), 200
        except Exception as e:
            print('Erro:', e)
            return jsonify({'message': 'Internal server error'}), 500
            
    def add_user(self):
        ...
        
    def update_user(self):
        ...
        
    def delete_user(self):
        ...