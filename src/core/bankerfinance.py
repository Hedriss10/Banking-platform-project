from src.models.bankerfinance import BankerFinanceModels
from src.db.pg import PgAdmin
from src.service.response import Response
from src.utils.pagination import Pagination
from psycopg2.errors import UniqueViolation
from src.utils.log import setup_logger

logger = setup_logger(__name__)


class BankerFinanceCore:

    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        self.models = BankerFinanceModels(user_id=user_id)
        self.pg = PgAdmin()

    def list_bankers(self, data: dict):
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

        bankers = self.pg.fetch_to_dict(query=self.models.list_bankers(pagination=pagination))

        if not bankers:
            logger.warning(f"Bankers List Not Found.")
            return Response().response(status_code=404, error=True, message_id="bankers_list_not_found", exception="Not found", data=bankers)

        metadata = Pagination().metadata(current_page=current_page, rows_per_page=rows_per_page, sort_by=pagination["sort_by"], order_by=pagination["order_by"], filter_by=pagination["filter_by"])
        return Response().response(status_code=200, message_id="bankers_list_bankers_successful", data=bankers, metadata=metadata)

    def get_banker(self, id: int):
        banker = self.pg.fetch_to_dict(query=self.models.get_banker(banker_id=id))
        if not banker:
            logger.warning(f"Banker Not Found.")
            return Response().response(status_code=404, error=True, message_id="banker_not_found", exception="Not found", data=banker)

        return Response().response(status_code=200, error=False, message_id="banker_get_successful", data=banker)

    def add_banker(self, data):
        try:
            if not data.get("name"):
                logger.warning(f"Banker Name Is Required.")
                return Response().response(status_code=400, error=True, message_id="banker_name_is_required", exception="Banker Name Is Required")

            banker = self.pg.fetch_to_dict(query=self.models.add_bankers(name=data.get("name")))
            self.pg.commit()
            return Response().response(status_code=200, error=False, message_id="banker_register_successful", data={"id": banker})

        except UniqueViolation:
            return Response().response(status_code=400, message_id="name_banker_already_exists", error=True, exception="Name Banker with this name already exists")
        
    def add_financial_agreements(self, data):
        try:
            if not data.get("name"):
                logger.warning(f"Finncial Agreements Name Is Required")
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="financial_agreements_is_required",
                    exception="Financial Agreements Name Is Required",
                )

            financial_agreements = self.pg.fetch_to_dict(query=self.models.add_financial_agreements(name=data.get("name"), banker_id=data.get("banker_id")))
            self.pg.commit()

            return Response().response(status_code=200, error=False, message_id="financial_agreements_successful", data={"id": financial_agreements})
        except Exception as e:
            logger.error(f"Error Adds financial agreements, {e}", exc_info=True)
            return Response().response(status_code=400, error=True, message_id="financial_agreements_add_error")
    
    def update_financial_agreements(self, id: int, data: dict):
        try: 
            try:
                if not data.get("name"):
                    logger.warning(f"Financial Agreements is Name Required.")
                    return Response().response(
                        status_code=401,
                        error=True,
                        message_id="financial_agreements_is_required",
                        exception="Financial Agreements Name Is Required",)

                financial_agreements = self.pg.fetch_to_dict(query=self.models.update_financial_agreements(name=data.get("name"), id=id))
                self.pg.commit()
                return Response().response(status_code=200, error=False, message_id="banker_update_successful", data={"id": financial_agreements})
            except Exception as e:
                return Response().response(status_code=200, error=True, message_id="banker_update_successful", data={"id": financial_agreements})
        except Exception as e:
            logger.error(f"Error Edit financial agreements, {e}", exc_info=True)
            return Response().response(status_code=400, error=True, message_id="financial_agreements_edit_error")

    def update_banker(self, id: int, data: dict):
        try:
            if not data.get("name"):
                logger.warning(f"Banker Name Is Required.")
                return Response().response(status_code=401, error=True, message_id="banker_name_is_required", exception="Banker Name Is Required")

            banker = self.pg.fetch_to_dict(query=self.models.update_bankers(name=data.get("name"), id=id))
            self.pg.commit()
            return Response().response(status_code=200, error=False, message_id="banker_update_successful", data={"id": banker})
        except UniqueViolation:
            return Response().response(status_code=400, message_id="name_banker_already_exists", error=True, exception="Name Banker with this name already exists")

    def delete_banker(self, id: int):
        try:
            if not id:
                logger.warning(f"Banker Id is Required.")
                return Response().response(status_code=401, error=True, message_id="banker_name_id_is_required", exception="Banker Id Is Required")
            
            bankers = self.pg.fetch_to_dict(query=self.models.delete_bankers(banker_id=id))
            print(bankers)
            if bankers[0]["banker_exists"] == True: 
                self.pg.commit()
                return Response().response(status_code=200, error=False, message_id="banker_delete_successful")
            else: 
                return Response().response(status_code=404, error=True, message_id="banker_not_found", exception="Banker Not Found")

        except Exception as e:
            return Response().response(status_code=401, error=True, message_id="erro_delete_banker")
        
        
    def delete_financial_agreements(self, id: int):
        try:                
            if not id:
                logger.warning(f"Financial Agreements is Required ID.")
                return Response().response(
                    status_code=401,
                    error=True,
                    message_id="financial_agreements_is_required",
                    exception="Financial Agreements Id Is Required",
                )

            financial_agreements = self.pg.fetch_to_dict(query=self.models.delete_financial_agreements(id=id))
            self.pg.commit()
            return Response().response(status_code=200, error=False, message_id="banker_delete_successful", data={"id": financial_agreements})        
        except Exception as e:
            logger.error(f"Error Delete financial agreements, {e}", exc_info=True)
            return Response().response(status_code=400, error=True, message_id="financial_agreements_delete_error")