
from src.db.database import db
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash


class User(db.Model):
    
    __tablename__ = "user"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cpf = db.Column(db.String(100), unique=True, nullable=True)
    username = db.Column(db.String(150), nullable=False)
    lastname = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(300), nullable=True)
    role = db.Column(db.String(200), nullable=True)
    typecontract = db.Column(db.String(30), nullable=False)
    session_token = db.Column(db.Text, nullable=True)
    is_admin = db.Column(db.Boolean, nullable=True)
    is_block = db.Column(db.Boolean, nullable=True)
    is_acctive = db.Column(db.Boolean, nullable=True)
    is_comission = db.Column(db.Boolean, nullable=True)
    create_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    is_first_acess = db.Column(db.Boolean, nullable=False)
    is_deleted = db.Column(db.Boolean, nullable=True, default=False)
    reset_password_at = db.Column(db.DateTime, nullable=True)
    reset_password_by = db.Column(db.Integer, nullable=True)
    action_reset_password_text = db.Column(db.Text, nullable=True)


    def __repr__(self):
        return f"<User {self.username}>"


class UserModels:

    def __init__(self, user_id: int, *args, **kwargs) -> None:
        self.user_id = user_id
        
    def list_users(self, pagination: dict):
        query = f"""
            SELECT 
                id,
                cpf,
                username,
                lastname,
                email,
                role,
                typecontract,
                is_deleted,
                is_block,
                TO_CHAR(create_at, 'YYYY-MM-DD') AS create_at
            FROM 
                public.user u
            WHERE u.is_deleted = false AND u.is_block = false
            ORDER BY u.id desc 
            OFFSET {pagination["offset"]} LIMIT {pagination["limit"]};
        """
        return query

    def get_user(self, id: int) -> None:
        query = f"""
            SELECT 
                u.id,
                u.cpf, 
                u.username, 
                u.lastname, 
                u.email, 
                u.role,
                typecontract,
                TO_CHAR(create_at, 'YYYY-MM-DD') AS create_at,
                ep.matricula,
                ep.carga_horaria_semanal,
                ep.situacao_cadastro
            FROM 
                public.user u
                INNER JOIN public.employee ep ON u.id = ep.user_id
            WHERE u.id = {id} and u.is_deleted = false;
        """
        return query
        
    def add_user(self, data: dict, password: str):
        _cpf = data.get("cpf").replace(".", "").replace("-", "")
        
        query = f"""
            INSERT INTO public.user (username, lastname, email, password, role, typecontract, cpf, is_block, is_acctive, is_comission, is_first_acess, is_deleted) 
            VALUES (
                '{data.get("username")}',
                '{data.get("lastname")}',
                '{data.get("email")}',
                '{password}',
                '{data.get("role")}',
                '{data.get("typecontract")}',
                '{_cpf}',
                FALSE,
                TRUE,
                FALSE,
                TRUE,
                FALSE
            )
            RETURNING id; 
        """
        return query
    
    def add_employee(self, id: int, data: dict):
        """
            add employee id.
            columns: numero_pis, matricula, empresa, situacao_cadastro, carga_horaria_semanal, user_id, is_deleted
        Args:
            data (dict): _description_
        """
        _num = data.get("carga_horaria_semanal")
        query = f"""
            INSERT INTO employee(numero_pis, matricula, empresa, situacao_cadastro, carga_horaria_semanal, user_id, is_deleted) 
            VALUES ('{data.get("numero_pis")}', '{data.get("matricula")}', '{data.get("empresa")}', '{data.get("situacao_cadastro")}', {int(_num)}, {id}, false);
        """
        return query
                
    def update_user(self, id: int, data: dict):
        """
            Updates a user in the appropriate table based on the provided data.
        Args:
            id (int): User ID to update.
            data (dict): Fields and values to update.
        """
        fields_by_table = {
            "public.user": [
                "username", "lastname", "email", "cpf", "password", "typecontract",
                "role", "is_admin", "is_block", "is_acctive", "is_first_acess"
            ],
            "employee": [
                "matricula", "numero_pis", "empresa", "situacao_cadastro", "carga_horaria_semanal"
            ]
        }

        updates = {table: [] for table in fields_by_table.keys()}

        for key, value in data.items():
            for table, fields in fields_by_table.items():
                if key in fields and value is not None:
                    if table == "public.user" and key == "cpf":
                        value = value.replace(".", "").replace("-", "")
                    elif table == "public.user" and key == "password":
                        value = generate_password_hash(password=value, method="scrypt")

                    formatted_value = f"'{value}'" if isinstance(value, str) else value
                    updates[table].append(f"{key} = {formatted_value}")

        queries = []
        for table, set_clauses in updates.items():
            if set_clauses:
                set_clause_str = ", ".join(set_clauses)

                if table == "employee":
                    where_clause = f"user_id = {id}"
                else:
                    where_clause = f"id = {id}"

                query = f"""
                    UPDATE {table} 
                    SET {set_clause_str},
                        updated_at = now()
                    WHERE {where_clause};
                """
                queries.append(query)
        
        return queries

    def delete_user(self, id):
        query = f"""
            UPDATE public.user u
            SET
                is_deleted = true,
                is_acctive = false
            WHERE u.id = {id}
            RETURNING u.id;
        """
        return query
        