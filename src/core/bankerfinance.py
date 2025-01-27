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
        banker = self.pg.fetch_to_dict(query=self.models.get_banker(id=id))
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
            banker = self.pg.fetch_to_dict(query=self.models.delete_bankers(id=id))
            self.pg.commit()
            return Response().response(status_code=200, error=False, message_id="banker_delete_successful", data={"id": banker})
        except Exception as e:
            return Response().response(status_code=401, error=True, message_id="erro_delete_banker")