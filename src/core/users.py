from src.models.users import UserModels
from src.db.pg import PgAdmin
from src.service.response import Response
from src.utils.pagination import Pagination
from werkzeug.security import generate_password_hash
from psycopg2.errors import UniqueViolation
from src.utils.log import setup_logger

log = setup_logger(__name__)


class UsersCore:

    def __init__(self, user_id: int, *args, **kwargs) -> None:
        self.pg = PgAdmin()
        self.model = UserModels(user_id)
        self.user_id = user_id

    def list_users(self, data: dict):
        current_page, rows_per_page = int(data.get("current_page", 1)), int(
            data.get("rows_per_page", 10))

        if current_page < 1:
            current_page = 1
        if rows_per_page < 1:
            rows_per_page = 1

        pagination = Pagination().pagination(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=data.get("sort_by", ""),
            order_by=data.get("order_by", ""),
            filter_by=data.get("filter_by", "")
        )

        users = self.pg.fetch_to_dict(query=self.model.list_users(pagination=pagination))

        if not users:
            return Response().response(status_code=404, error=True, message_id="users_list_not_found", exception="Not found", data=users)

        metadata = Pagination().metadata(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=pagination["sort_by"],
            order_by=pagination["order_by"],
            filter_by=pagination["filter_by"]
        )
        return Response().response(status_code=200, message_id="users_list_users_successful", data=users, metadata=metadata)

    def get_user(self, id):
        user = self.pg.fetch_to_dict(query=self.model.get_user(id=id))
        
        if not user:
            return Response().response(status_code=404, error=True, message_id="user_get_not_found", exception="Not found", data=user)
        
        return Response().response(status_code=200, message_id="user_get_successful", data=user)

    def add_user(self, data: dict):
        try:
            if not data.get("cpf"):
                return Response().response(status_code=400, message_id="cpf_is_required", exception="CPF is required")
            
            password = data.get("password")
            hashed_password = generate_password_hash(password, method="scrypt") if password else None

            user = self.pg.fetch_to_dict(query=self.model.add_user(data=data, password=hashed_password))            
            employee_user = self.pg.execute_query(query=self.model.add_employee(id=user[0]["id"], data=data ))
            
            if not user or employee_user:
                return Response().response(status_code=400, message_id="bad_is_request", exception="Bad request", data=user)
            
            self.pg.commit()
            return Response().response(status_code=200, message_id="user_add_successful", metadata={"dict": data})

        except UniqueViolation:
            return Response().response(status_code=400, message_id="cpf_with_email_already_exists", error=True, exception="CPF with this cpf already exists")
        
    def update_user(self, id: int, data):
        try:
            if not id and data:
                log.warning("Bad request id or data is required")
                return Response().response(status_code=400, message_id="id_or_data_is_required", exception="ID or Data is required")
            
            users = self.model.update_user(id=id, data=data)
            for user in users:
                self.pg.execute_query(query=user)
                
            self.pg.commit()
            return Response().response(status_code=200, message_id="user_edit_successful")
        
        except UniqueViolation:
            log.error(f"Error eidt user cpf duplicate {e}", exc_info=True)
            return Response().response(status_code=400, message_id="cpf_with_email_already_exists", error=True, exception="CPF with this cpf already exists")
        
        except Exception as e:
            log.error(f"Error edit user {e}", exc_info=True)
            return Response().response(status_code=400, message_id="error_edit_user", error=True, exception="bad request")
        
    def delete_user(self, id):
        user = self.pg.fetch_to_dict(query=self.model.delete_user(id=id))
        if not user:
            return Response().response(status_code=404, error=True, message_id="user_get_not_found", exception="Not found", data=user)
        self.pg.commit()
        return Response().response(status_code=200, message_id="user_delete_successful", data=user)