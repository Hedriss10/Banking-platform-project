from werkzeug.security import generate_password_hash

class UserModels:

    def __init__(self, user_id: int, *args, **kwargs) -> None:
        self.user_id = user_id
        
    def list_users(self, pagination: dict):
        query_filter = ""
        if pagination["filter_by"]:
            query_filter = f"""AND (unaccent(u.username) ILIKE unaccent('%{pagination["filter_by"]}%')) OR (unaccent(u.cpf) ILIKE unaccent('%{pagination["filter_by"]}%'))"""
        
        query_order_by = ""
        if pagination["sort_by"] and pagination["order_by"]:
            query_order_by = f"""ORDER BY u.{pagination["order_by"]} {pagination["sort_by"]}"""

        query = f"""
            SELECT 
                id,
                cpf,
                username,
                lastname,
                email,
                role,
                typecontract,
                is_first_acess,
                is_deleted,
                is_block,
                is_acctive,
                TO_CHAR(create_at, 'YYYY-MM-DD') AS create_at
            FROM 
                public.user u
            WHERE u.is_deleted = false AND u.is_block = false {query_filter}
            ORDER BY u.id desc 
            OFFSET {pagination["offset"]} LIMIT {pagination["limit"]};
        """
        return query

    def get_user(self, id: int) -> None:
        query = f"""
            SELECT 
                id,
                cpf, 
                username, 
                lastname, 
                email, 
                role,
                is_first_acess,
                typecontract,
                TO_CHAR(create_at, 'YYYY-MM-DD') AS create_at
            FROM 
                public.user u
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
        