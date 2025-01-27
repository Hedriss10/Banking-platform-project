from src.models.financialagreements import FinancialAgreementsModels
from src.db.pg import PgAdmin
from src.service.response import Response
from src.utils.pagination import Pagination
from src.utils.log import setup_logger

logger = setup_logger(__name__)


class FinancialAgreementsCore:

    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.models = FinancialAgreementsModels(user_id=user_id)
        self.pg = PgAdmin()

    def list_financial_agreements(self, data: dict):
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
            filter_by=data.get("filter_by", ""),
        )

        rows = self.pg.fetch_to_dict(query=self.models.list_financial_agreements(pagination=pagination))
        result = {}

        for row in rows:
            banker = row['banker']
            if banker not in result:
                result[banker] = {'banker_id': row['banker_id'], 'financial_agreements': []}
            result[banker]['financial_agreements'].append({'id': row['id_financial_agreements'], 'name': row['financial_agreements']})

        if not rows:
            logger.warning(f"Financial Agreements List Not Found.")
            return Response().response(status_code=404, error=True, message_id="financial_agreements_list_not_found", exception="Not found", data=rows)

        metadata = Pagination().metadata(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=pagination["sort_by"],
            order_by=pagination["order_by"],
            filter_by=pagination["filter_by"],
        )
        return Response().response(status_code=200, message_id="financial_agreements_list_bankers_successful", data=result, metadata=metadata)

    def get_financial_agreements(self, id: int):
        financial_agreements = self.pg.fetch_to_dict(query=self.models.get_financial_agreements(id=id))

        if not financial_agreements:
            logger.warning(f"FinancialAgreements Not Found")
            return Response().response(
                status_code=404,
                error=True,
                message_id="financial_agreements_found",
                exception="Not found",
                data=financial_agreements,
            )

        return Response().response(status_code=200, error=False, message_id="financial_agreements_successful", data=financial_agreements)

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
                        exception="Financial Agreements Name Is Required",
                    )

                financial_agreements = self.pg.fetch_to_dict(query=self.models.update_financial_agreements(name=data.get("name"), id=id))
                self.pg.commit()
                return Response().response(status_code=200, error=False, message_id="banker_update_successful", data={"id": financial_agreements})
            except Exception as e:
                return Response().response(status_code=200, error=True, message_id="banker_update_successful", data={"id": financial_agreements})
        except Exception as e:
            logger.error(f"Error Edit financial agreements, {e}", exc_info=True)
            return Response().response(status_code=400, error=True, message_id="financial_agreements_edit_error")

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