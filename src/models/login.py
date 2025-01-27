import json

class LoginModels:
    
    def __init__(self, email: str, user_id: int, *args, **kwargs):
        self.email = email
        self.user_id = user_id
    
    def add_session_token(self, token: str, id: int):
        query = f"""
            UPDATE public.user
            SET
                session_token='{token}'
            WHERE id = {id};
        """
        return query
    
    def get_user_login(self, email: str):
        query = f"""
            SELECT
                id,
                password,
                email
            FROM 
                public."user" u 
            WHERE email='{email}';   
        """    
        return query
    
    def get_user_list_info(self, id: int):
        query = f"""
            SELECT
                u.id,
                e.id as employee_id,
                u.cpf,
                u.username,
                u.lastname,
                u.email,
                u.role,
                u.typecontract,
                u.is_first_acess,
                u.is_deleted,
                u.is_acctive,
                e.matricula,
                e.numero_pis,
                e.situacao_cadastro,
                e.carga_horaria_semanal,
                u.is_admin,
                u.is_block,
                u.is_comission,
                TO_CHAR(u.create_at, 'YYYY-MM-DD') AS create_at
            FROM 
                public.user u
                LEFT JOIN employee e on u.id = e.user_id	
            WHERE u.id = {id}
        """
        return query
    
    def get_email(self, email) -> None:
        query = f"""
            SELECT email FROM public.user WHERE email='{email}';
        """
        return query
    
    def reset_password(self, email: str, password: str):
        query = f"""
            UPDATE public.user
            SET
                password='{password}',
                is_first_acess = false
            WHERE email = '{email}';
        """
        return query
    
    def reset_password_master(self, id: int, password: str, user_id: int):
        logs = {"user_id": user_id, "reset": "This was reset by the master"}
        
        query = f"""
            UPDATE public.user
            SET
                is_first_acess=true,
                password='{password}',
                reset_password_by = {user_id},
                reset_password_at = NOW(),
                action_reset_password_text = ARRAY['{json.dumps({'action': 'insert', 'user_id': user_id, **logs})}']
            WHERE id = {id}
            RETURNING id;
        """
        return query