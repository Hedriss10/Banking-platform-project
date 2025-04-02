import traceback

from psycopg2.errors import UniqueViolation

from src.db.pg import PgAdmin
from src.models.flag import FlagsModels
from src.service.response import Response
from src.utils.log import logdb
from src.utils.pagination import Pagination


class FlagsCore:

    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.pg = PgAdmin()
        self.models = FlagsModels(user_id=user_id)

    def list_flags(self, data: dict) -> None:
        try:
            current_page, rows_per_page = int(data.get("current_page", 1)), int(data.get("rows_per_page", 10))

            if current_page < 1:  # Force variables min values
                current_page = 1
            if rows_per_page < 1:
                rows_per_page = 1

            pagination = Pagination().pagination(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=data.get("sort_by", ""),
                order_by=data.get("order_by", ""),
                filter_by=data.get("filter_by", ""),
            )

            flags = self.pg.fetch_to_dict(query=self.models.list_flags(pagination=pagination))

            if not flags:
                return Response().response(status_code=404, error=True, message_id="flags_not_found", exception="Not found", data=flags)

            metadata = Pagination().metadata(
                current_page=current_page, 
                rows_per_page=rows_per_page, 
                sort_by=pagination["sort_by"], 
                order_by=pagination["order_by"], 
                filter_by=pagination["filter_by"])
            return Response().response(status_code=200, message_id="list_flags_sucessful", data=flags, metadata=metadata)
        except Exception as e:
            logdb("error", message=f"Error check report proposal. {e}")
            return Response().response(status_code=400, error=True, message_id="error_check_report_proposal", exception=str(e), traceback=traceback.format_exc(e))
        
        
    def add_flags(self, data: dict):
        try:
            if not data.get("name"):
                return Response().response(status_code=400, error=True, message_id="name_is_required", exception="Name is required")

            self.pg.execute_query(query=self.models.add_flag(data=data))
            self.pg.commit()
            return Response().response(status_code=200, error=False, message_id="add_flags_successfully")
        except UniqueViolation:
            return Response().response(status_code=409, error=True, message_id="name_already_exists")
        except Exception as e:
            print(e)
            return Response().response(status_code=400, error=True, message_id="erro_processing", exception=str(e))

    def delete_flag(self, data: dict):
        try:
            if not data.get("ids"):
                return Response().response(status_code=400, error=True, message_id="id_is_required", exception="Ids is required")

            self.pg.execute_query(query=self.models.delete_flag(ids=data.get("ids")))
            self.pg.commit()
            return Response().response(status_code=200, error=False, message_id="delete_flags_successfully")
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="erro_processing", exception=str(e))
