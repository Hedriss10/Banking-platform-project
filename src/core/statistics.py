from src.models.statistics import StatisticsModel
from src.service.response import Response
from src.utils.log import logdb
from src.utils.pagination import Pagination
from src.db.pg import PgAdmin

class StatisticsCore:
    
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.models = StatisticsModel(user_id=user_id)
        self.pg = PgAdmin()

    def list_hold_profit_sellers(self, data: dict):
        try:
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

            list_rank_tables = self.pg.fetch_to_dict(query=self.models.list_hold_profit_sellers(pagination=pagination))
            if not list_rank_tables:
                return Response().response(status_code=404, error=True, message_id="list_profit_list_not_found", exception="Not found", data=list_rank_tables)
            
            metadata = Pagination().metadata(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=pagination["sort_by"],
                order_by=pagination["order_by"],
                filter_by=pagination["filter_by"]
            )
            return Response().response(status_code=200, message_id="list_profit_successful", data=list_rank_tables, metadata=metadata)
            
        except Exception as e:
            logdb("error", message=f"Error processing loan operation. {e}")
            return Response().response(status_code=400, error=True, message_id="list_rank_tables_ranks", exception=str(e))
        