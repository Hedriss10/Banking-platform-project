# src/core/datacatalog.py
from datetime import datetime

from sqlalchemy import func, select, or_
from src.db.database import db
from src.models.models import Benefit, Bank, LoanOperation
from src.service.response import Response
from src.utils.log import logdb
from src.utils.metadata import Metadata
from src.utils.pagination import Pagination


class DataCatalogBenefit:
    """ Manage CRUD benefit operations
        - list
        - add
        - delete
    Args:
        user_id (int): users id
        
    Returns:
        _type_: _description_
    """
    
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.benefit = Benefit
        
        
    def add_benefit(self, data: dict):
        try:
            name = data.get("name")            
            if not name:
                return Response().response(
                status_code=400, 
                error=True, 
                message_id="name_is_required", 
                exception="Name is required"
            )
            
            benefit = self.benefit(
                name=name,
                created_at=datetime.now()
            )
            db.session.add(benefit)
            db.session.commit()
            return Response().response(
                status_code=200, 
                message_id="benefit_add_successful",
                error=False
            )
        
        except Exception as e:
            logdb("error", message=f"Error processing add benefit. {e}")
            return Response().response(
            status_code=400,
            error=True, 
            message_id="error_processing_benefit", 
            exception=str()
        )
    
    def list_benefit(self, data: dict):
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
            stmt = select(
                self.benefit.id, 
                self.benefit.name
            ).where(self.benefit.is_deleted == False)
            
            # Ordenação dinâmica
            if pagination["order_by"] and pagination["sort_by"]:
                sort_column = getattr(self.benefit, pagination["order_by"], None)
                if sort_column:
                    if pagination["sort_by"] == "asc":
                        stmt = stmt.order_by(sort_column.asc())
                    else:
                        stmt = stmt.order_by(sort_column.desc())
            else:
                stmt = stmt.order_by(self.benefit.id.desc())
            
            
            # Paginação
            offset = pagination["offset"]
            limit = pagination["limit"]

            paginated_stmt = stmt.offset(offset).limit(limit)
            results = db.session.execute(paginated_stmt).fetchall()
                        
            if not results:
                return Response().response(
                status_code=404, 
                error=True, 
                message_id="list_benefit_list_not_found", 
                exception="Not found"
            )
            
            total = db.session.execute(
                select(func.count(self.benefit.id)).where(self.benefit.is_deleted == False)
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
                message_id="benefit_list_successful", 
                data=Metadata(results).model_to_list(), 
                metadata=metadata,
                error=False,
            )
            
        except Exception as e:
            logdb("error", message=f"Error processing list benefit. {e}")
            return Response().response(
            status_code=500, 
            error=True, 
            message_id="error_list_benefit", 
            exception=str(e)
        )
        
    def delete_benefit(self, id: int):
        try:
            if not id:
                return Response().response(
                status_code=400, 
                error=True, 
                message_id="id_is_required", 
                exception="Id is required"
            )
            
            benefit = self.benefit.query.filter_by(id=id).first()
            benefit.is_deleted = True
            benefit.deleted_by = self.user_id
            self.benefit.query.session.commit()        
            return Response().response(
                status_code=200, 
                message_id="benifit_delete_successful",
                error=False
            )
        
        except Exception as e:
            logdb("error", message=f"Error processing deleted benefit. {e}")
            return Response().response(
                status_code=500, 
                error=True, 
                message_id="error_loan_opeartion", 
                exception=str(e)
            )

class DataCatalogBank:
    """ Manage Bank Crud Operations
        - list
        - add
        - delete
    Args:
        user_id (int): users id
        
    Returns:
        _type_: _description_
    """

    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.bank = Bank
        
    
    def add_bank(self, data: dict):
        try:
            name = data.get("name")
            id_bank = data.get("id_bank")
            if not name:
                return Response().response(
                    status_code=400, 
                    error=True, 
                    message_id="name_is_required", 
                    exception="Name is required"
                )

            bank = self.bank(
                name=name,
                id_bank=id_bank
            )
            db.session.add(bank)
            db.session.commit()

            return Response().response(
                status_code=200, 
                message_id="bank_add_successful",
                error=False
            )
        
        except Exception as e:
            db.session.rollback()
            logdb("error", message=f"Error processing add bank. {e}")
            return Response().response(
                status_code=500, 
                error=True, 
                message_id="error_bank_add", 
                exception=str(e)
            )
    
    def list_bank(self, data: dict):
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

            stmt = select(
                self.bank.id,
                self.bank.name,
            ).where(self.bank.is_deleted == False)
            
            
            # Filtro dinâmico com ILIKE + unaccent
            if pagination["filter_value"]:
                filter_value = f"%{pagination['filter_value']}%"
                stmt = stmt.where(
                    or_(
                        func.unaccent(self.bank.name).ilike(func.unaccent(filter_value))
                    )
                )

            if pagination["sort_by"]:
                sort_column = getattr(self.bank, pagination["sort_by"])
                if pagination["order_by"] == "asc":
                    stmt = stmt.order_by(sort_column.asc())
                else:
                    stmt = stmt.order_by(sort_column.desc())
            else:
                stmt = stmt.order_by(self.bank.id.desc())
            
            # Paginação
            offset = pagination["offset"]
            limit = pagination["limit"]

            paginated_stmt = stmt.offset(offset).limit(limit)
            results = db.session.execute(paginated_stmt).fetchall()
            
            if not results:
                return Response().response(
                    status_code=404, 
                    error=True, 
                    message_id="list_banks_list_not_found", 
                    exception="Not found"
                )
            
            total = db.session.execute(
                select(func.count(self.bank.id)).where(self.bank.is_deleted == False)
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
                message_id="list_banks_list_successful", 
                data=Metadata(results).model_to_list(), 
                metadata=metadata,
                error=False
            )
            
        except Exception as e:
            logdb("error", message=f"Error processing list bank. {e}")
            return Response().response(status_code=400, error=True, message_id="error_list_bank", exception=str(e))

    def delete_bank(self, id: int):
        try:
            if not id:
                return Response().response(
                    status_code=400, 
                    error=True, 
                    message_id="id_is_required", 
                    exception="Id is required"
                )
            bank = self.bank.query.filter_by(id=id).first()
            
            if not bank:
                return Response().response(
                    status_code=400, 
                    error=True, 
                    message_id="bank_not_found", 
                    exception="Bank not found"
                )
            
            bank.is_deleted = True
            bank.deleted_by = self.user_id
            bank.deleted_at = datetime.now()
            db.session.commit()
            
            return Response().response(
                status_code=200, 
                message_id="bank_delete_successful", 
                error=False
            )
        except Exception as e:
            logdb("error", message=f"Error processing loan operation. {e}")
            return Response().response(status_code=400, error=True, message_id="error_bank_delete", exception=str(e))

class DataCatalogLoanOperation:
    ### TODO - realizar as mudanças para SQlAlchemy
    """
        Manage Loan Operation Crud Operations
        - list
        - add
        - delete
    args:
        user_id (int): users id
    Returns:
        _type_: _description_
    """
    
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
    
    
    def list_loan_operation(self, data: dict):
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
                filter_by=data.get("filter_by", "")
            )

            loan_operation = self.pg.fetch_to_dict(query=self.models.list_loan_operation(pagination=pagination))
            
            if not loan_operation:
                return Response().response(status_code=404, error=True, message_id="loan_operation_list_not_found", exception="Not found", data=loan_operation)
            
            metadata = Pagination().metadata(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=pagination["sort_by"],
                order_by=pagination["order_by"],
                filter_by=pagination["filter_by"]
            )
            
            return Response().response(status_code=200, message_id="loan_operation_list_successful", data=loan_operation, metadata=metadata)
            
        except Exception as e:
            logdb("error", message=f"Error processing loan operation. {e}")
            return Response().response(status_code=400, error=True, message_id="error_loan_opeartion", exception=str(e))
           
    def add_loan_operation(self, data: dict):
        name = data.get("name")
        try:
            if not name:
                return Response().response(status_code=400, error=True, message_id="name_is_required", exception="Name is required")
            
            loan_operation = self.pg.fetch_to_dict(query=self.models.add_loan_operation(name=name))
            self.pg.commit()
            return Response().response(status_code=200, message_id="loan_operation_add_successful", data={"name": loan_operation})
        
        except Exception as e:
            logdb("error", message=f"Error processing loan operation. {e}")
            return Response().response(status_code=400, error=True, message_id="error_loan_opeartion", exception=str(e))
        
    def delete_loan_operation(self, id: int):
        try:
            self.pg.execute_query(query=self.models.delete_loan_operation(id=id))
            self.pg.commit()
        
            return Response().response(status_code=200, message_id="loan_operation_delete_successful")
        
        except Exception as e:
            logdb("error", message=f"Error processing loan operation. {e}")
            return Response().response(status_code=400, error=True, message_id="error_loan_opeartion", exception=str(e))
     