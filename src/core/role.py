# src/core/role.py
from psycopg2.errors import UniqueViolation
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from src.db.database import db
from src.models.models import Role
from src.service.response import Response
from src.utils.log import logdb
from src.utils.metadata import Metadata
from src.utils.pagination import Pagination


class RoleCore:
    
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.role = Role


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

        stmt = select(
            self.role.id,
            func.initcap(func.trim(self.role.name)).label('name')
        ).where(self.role.is_deleted == False)

        if pagination["filter_value"]:
            filter_value = f"%{pagination['filter_value']}%"
            query = query.filter(
                db.or_(
                    func.unaccent(self.role.name).ilike(func.unaccent(filter_value)),
                )
            )
            
        # Paginação
        offset = pagination["offset"]
        limit = pagination["limit"]

        paginated_stmt = stmt.offset(offset).limit(limit)
        results = db.session.execute(paginated_stmt).fetchall()
        
        if not results:
            return Response().response(
                status_code=404, 
                error=True, 
                message_id="role_list_not_found", 
                exception="Not found",
            )

        total = db.session.execute(
            select(func.count(self.role.id)).where(self.role.is_deleted == False)
        ).scalar()


        metadata = Pagination().metadata(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=pagination["sort_by"],
            order_by=pagination["order_by"],
            filter_by=pagination["filter_by"],
            total=total
        )
        return Response().response(
            status_code=200, 
            message_id="role_list_successful", 
            data=Metadata(results).model_to_list(),  
            metadata=metadata)
        
    def add_role(self, data: dict):
        try:
            if not data or not data.get("name"):
                return Response().response(
                    status_code=400,
                    message_id="role_is_name_required",
                    exception="Name role is required"
                )

            role = self.role(name=data.get("name"))
            self.role.query.session.add(role)
            self.role.query.session.commit()
            
            return Response().response(
                status_code=200,
                error=False,
                message_id="add_role_succesfully",
            )

        except IntegrityError as e:
            if isinstance(e.orig, UniqueViolation):
                logdb("warning", message="Role name already exists")
                self.role.query.session.rollback()
                return Response().response(
                    status_code=400,
                    message_id="role_name_already_exists"
                )
            else:
                self.role.query.session.rollback()
                logdb("error", message=f"Integrity error: {e}")
                return Response().response(
                    status_code=400,
                    message_id="role_integrity_error",
                    exception=str(e)
                )

        except Exception as e:
            self.role.query.session.rollback()
            logdb("error", message=f"Error adding role: {e}")
            return Response().response(
                status_code=500,
                message_id="role_error",
                exception=str(e)
            )
        
    def delete_role(self, id: int):
        try:
            role = self.role.query.filter_by(id=id).update({"is_deleted": True})
            if not role:
                return Response().response(
                    status_code=404,
                    error=True,
                    message_id="role_delete_not_found",
                    exception="Not found"
                )
                
            self.role.query.session.commit()
            return Response().response(
                status_code=200,
                message_id="role_delete_successful"
            )
        except Exception as e:
            self.role.query.session.rollback()
            logdb("error", message=f"Error deleting role: {e}")
            return Response().response(
                status_code=500,
                message_id="role_error",
                exception=str(e)
            )