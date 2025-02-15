from src.models.role import RoleModel
from src.db.pg import PgAdmin
from src.service.response import Response
from src.utils.pagination import Pagination
from src.utils.log import setup_logger
from psycopg2.errors import UniqueViolation


logger = setup_logger(__name__)

class RoleCore:
    
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.models = RoleModel(user_id=user_id)
        self.pg = PgAdmin()
        
    def list_role(self, data: dict):
        current_page, rows_per_page = int(data.get("current_page", 1)), int(data.get("rows_per_page", 10))

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

        role = self.pg.fetch_to_dict(query=self.models.list_role(pagination=pagination))
        
        if not role:
            logger.warning(f"Role List Not Found.")
            return Response().response(status_code=404, error=True, message_id="role_list_not_found", exception="Not found", data=role)

        metadata = Pagination().metadata(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=pagination["sort_by"],
            order_by=pagination["order_by"],
            filter_by=pagination["filter_by"]
        )
        return Response().response(status_code=200, message_id="role_list_successful", data=role,  metadata=metadata)
        
    def add_role(self, data: dict):
        try:
            if not data:
                return Response().response(status_code=400, message_id="role_is_name_required", exception="Name role is required")
            self.pg.execute_query(query=self.models.add_role(data=data))
            self.pg.commit()
            return Response().response(status_code=200, message_id="add_role_succesfully")
        except UniqueViolation:
            return Response().response(status_code=400, message_id="role_name_already_exists")
        except Exception as e:
            return Response().response(status_code=500, message_id="role_error", exception=str(e))
    
    def delete_role(self, id: int):
        try:
            if not id:
                return Response().response(status_code=400, message_id="role_is_id_required", exception="Name id is required")
            self.pg.execute_query(query=self.models.delete_role(id=id))
            self.pg.commit()
            return Response().response(status_code=200, message_id="delete_role_succesfully")
        except Exception as e:
            return Response().response(status_code=400, message_id="role_error")