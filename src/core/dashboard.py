
from src.db.pg import PgAdmin
from src.models.dashboard import DashBoardModels
from src.service.response import Response
from src.utils.log import logdb
from src.utils.pagination import Pagination


class DashBoardsCore:
    
    def __init__(self, user_id: int, *args, **kwargs) -> None:
        self.user_id = user_id
        self.pg = PgAdmin()
        self.models = DashBoardModels(user_id=user_id)
        
    def sales_paid(self) -> None:
        try:
            sales_paid = self.pg.fetch_to_dict(query=self.models.sales_paid())
            return Response().response(status_code=200, error=False, message_id="sales_paid_success", data=sales_paid)
        except Exception as e:
            logdb("error", message=f"Error processing Dasboard. {e}")
            return Response().response(status_code=500, error=True, message_id="error_processs_dashboard", exception=str(e))

    def status_proposals(self) -> None:
        try:
            status_proposal = self.pg.fetch_to_dict(query=self.models.status_proposals())
            return Response().response(status_code=200, error=False, message_id="status_proposals_success", data=status_proposal)   
        except Exception as e:
            logdb("error", message=f"Error processing Dashbaord. {e}")
            return Response().response(status_code=500, error=True, message_id="error_processs_dashboard", exception=str(e))
        
    def salles_sales_paid_ranking(self, data: dict) -> None:
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

            ranking = self.pg.fetch_to_dict(query=self.models.salles_sales_paid_ranking(pagination=pagination))
            
            metadata = Pagination().metadata(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=pagination["sort_by"],
                order_by=pagination["order_by"],
                filter_by=pagination["filter_by"]
            )
            return Response().response(status_code=200, error=False, message_id="ranking_success", data=ranking, metadata=metadata)
        except Exception as e:
            logdb("error", message=f"Error processing Dashbaord. {e}")
            return Response().response(status_code=500, error=True, message_id="error_processs_dashboard", exception=str(e))