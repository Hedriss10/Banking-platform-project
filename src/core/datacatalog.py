from src.db.pg import PgAdmin
from src.models.datacatalog import DataCatalogModels
from src.service.response import Response
from src.utils.log import logdb
from src.utils.pagination import Pagination


class DataCatalogCore:

    def __init__(self, user_id: int, *args, **kwargs) -> None:
        self.user_id = user_id
        self.models = DataCatalogModels(user_id=user_id)
        self.pg = PgAdmin()
        
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
        
    def list_rank_tables(self, data: dict):
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

            list_rank_tables = self.pg.fetch_to_dict(query=self.models.list_rank_tables(pagination=pagination))
            
            if not list_rank_tables:
                return Response().response(status_code=404, error=True, message_id="list_rank_tables_list_not_found", exception="Not found", data=list_rank_tables)
            
            metadata = Pagination().metadata(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=pagination["sort_by"],
                order_by=pagination["order_by"],
                filter_by=pagination["filter_by"]
            )
            return Response().response(status_code=200, message_id="list_rank_tables_list_successful", data=list_rank_tables, metadata=metadata)
            
        except Exception as e:
            logdb("error", message=f"Error processing loan operation. {e}")
            return Response().response(status_code=400, error=True, message_id="list_rank_tables_ranks", exception=str(e))
        
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
                filter_by=data.get("filter_by", "")
            )

            list_benefit = self.pg.fetch_to_dict(query=self.models.list_benefit(pagination=pagination))
            
            if not list_benefit:
                return Response().response(status_code=404, error=True, message_id="loan_benefit_list_not_found", exception="Not found", data=list_benefit)
            
            metadata = Pagination().metadata(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=pagination["sort_by"],
                order_by=pagination["order_by"],
                filter_by=pagination["filter_by"]
            )
            
            return Response().response(status_code=200, message_id="loan_benefit_list_successful", data=list_benefit, metadata=metadata)
            
        except Exception as e:
            logdb("error", message=f"Error processing loan operation. {e}")
            return Response().response(status_code=400, error=True, message_id="error_loan_opeartion", exception=str(e))
        
    def add_benefit(self, data: dict):
        name = data.get("name")
        try:
            if not name:
                return Response().response(status_code=400, error=True, message_id="name_is_required", exception="Name is required")
            
            loan_operation = self.pg.fetch_to_dict(query=self.models.add_benefit(name=name))
            self.pg.commit()
            return Response().response(status_code=200, message_id="benefit_add_successful", data={"name": loan_operation})
        
        except Exception as e:
            logdb("error", message=f"Error processing loan operation. {e}")
            return Response().response(status_code=400, error=True, message_id="error_befinit_opeartion", exception=str())
        
    def delete_benefit(self, id: int):
        try:
            self.pg.execute_query(query=self.models.delete_benefit(id=id))
            self.pg.commit()
        
            return Response().response(status_code=200, message_id="benifit_delete_successful")
        
        except Exception as e:
            logdb("error", message=f"Error processing loan operation. {e}")
            return Response().response(status_code=400, error=True, message_id="error_loan_opeartion", exception=str(e))

    def add_bank(self, data: dict):
        name = data.get("name")
        id_bank = data.get("id_bank")
        try:
            if not name:
                return Response().response(status_code=400, error=True, message_id="name_is_required", exception="Name is required")
            
            bank = self.pg.fetch_to_dict(query=self.models.add_bank(name=name, id_bank=id_bank))
            self.pg.commit()
            return Response().response(status_code=200, message_id="bank_add_successful", data={"name": bank})
        
        except Exception as e:
            logdb("error", message=f"Error processing loan operation. {e}")
            return Response().response(status_code=400, error=True, message_id="error_bank_add", exception=str(e))
    
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
                filter_by=data.get("filter_by", "")
            )

            list_banks = self.pg.fetch_to_dict(query=self.models.list_banks(pagination=pagination))
            
            if not list_banks:
                return Response().response(status_code=404, error=True, message_id="list_banks_list_not_found", exception="Not found", data=list_banks)
            
            metadata = Pagination().metadata(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=pagination["sort_by"],
                order_by=pagination["order_by"],
                filter_by=pagination["filter_by"]
            )
            
            return Response().response(status_code=200, message_id="list_banks_list_successful", data=list_banks, metadata=metadata)
            
        except Exception as e:
            logdb("error", message=f"Error processing loan operation. {e}")
            return Response().response(status_code=400, error=True, message_id="error_list_bank", exception=str(e))
    
    def delete_bank(self, id: int):
        try:
            self.pg.execute_query(query=self.models.delete_bank(id=id))
            self.pg.commit()
        
            return Response().response(status_code=200, message_id="bank_delete_successful")
        except Exception as e:
            logdb("error", message=f"Error processing loan operation. {e}")
            return Response().response(status_code=400, error=True, message_id="error_bank_delete", exception=str(e))
