# src/core/flag.py
import traceback

from psycopg2.errors import UniqueViolation
from sqlalchemy import func, select
from sqlalchemy.orm import aliased

from src.db.database import db
from src.models.models import Flag
from src.service.response import Response
from src.utils.log import logdb
from src.utils.metadata import Metadata, model_to_dict
from src.utils.pagination import Pagination


class FlagsCore:

    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.flag = Flag

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
                filter_value=data.get("filter_value", "")
            )
            
            Flag = aliased(self.flag)
            
            flags = self.flag.query.filter(self.flag.is_deleted == False).all()
            stmt = select(
                self.flag.id, 
                self.flag.name, 
                self.flag.rate,
                self.flag.created_by
            ).where(self.flag.is_deleted == False)

            # Paginação
            offset = pagination["offset"]
            limit = pagination["limit"]

            paginated_stmt = stmt.offset(offset).limit(limit)
            results = db.session.execute(paginated_stmt).fetchall()
            
            if not flags:
                return Response().response(
                status_code=404, 
                error=True, 
                message_id="flags_not_found", 
                exception="Not found", 
                data=flags
            )
            
            total = db.session.execute(
                select(func.count()).select_from(self.flag).where(self.flag.is_deleted == False)
            ).scalar()
                

            metadata = Pagination().metadata(
                current_page=current_page, 
                rows_per_page=rows_per_page, 
                sort_by=pagination["sort_by"], 
                order_by=pagination["order_by"], 
                filter_by=pagination["filter_by"],
                filter_value=pagination["filter_value"],
                total=total
            )
            
            return Response().response(
                status_code=200, 
                message_id="list_flags_sucessful", 
                data=Metadata(results).model_to_list(), 
                metadata=metadata,
                error=False
            )
        except Exception as e:
            logdb("error", message=f"Error check report proposal. {e}")
            return Response().response(status_code=400, error=True, message_id="error_check_report_proposal", exception=str(e), traceback=traceback.format_exc(e))
        
        
    def add_flags(self, data: dict):
        try:
            if not data.get("name"):
                return Response().response(status_code=400, error=True, message_id="name_is_required", exception="Name is required")
            flag = self.flag(name=data.get("name"), rate=data.get("rate"), created_by=self.user_id)
            self.flag.query.session.add(flag)
            self.flag.query.session.commit()
            return Response().response(status_code=200, error=False, message_id="add_flags_successfully", data=model_to_dict(flag))
        except UniqueViolation:
            return Response().response(status_code=409, error=True, message_id="name_already_exists")
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="erro_processing", exception=str(e))

    def delete_flag(self, data: dict):
        try:
            if not data.get("ids"):
                return Response().response(status_code=400, error=True, message_id="id_is_required", exception="Ids is required")
            
            flags = self.flag.query.filter(self.flag.id.in_(data.get("ids"))).all()
            if not flags:
                return Response().response(status_code=404, error=True, message_id="flags_not_found", exception="Not found")
            
            for flag in flags:
                flag.is_deleted = True
            self.flag.query.session.commit()
            return Response().response(status_code=200, error=False, message_id="delete_flags_successfully")
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="erro_processing", exception=str(e))

