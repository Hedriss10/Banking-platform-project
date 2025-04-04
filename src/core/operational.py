from src.db.pg import PgAdmin
from src.models.operational import OperationaModel
from src.service.response import Response
from src.utils.log import logdb
from src.utils.pagination import Pagination


class OperationalCore:

    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.models = OperationaModel(user_id=user_id)
        self.pg = PgAdmin()

    def typing_proposal(self, proposal_id: int, data: dict):
        ## TODO - ajustar depois novamente o financial_agreements_id
        try:
            if data.get("contrato_pago"):
                fields_proposal = self.pg.fetch_to_dict(query=self.models.check_summary_fields_proposal(proposal_id=proposal_id))

                if not fields_proposal or any(field.get(key) is None for field in fields_proposal for key in ["prazo_inicio", "prazo_fim", "valor_operacao",]):
                    return Response().response(
                        status_code=409,
                        error=True,
                        message_id="proposal_summary_and_validated_fields"
                    )
            self.pg.execute_query(
                query=self.models.typing_proposal(proposal_id=proposal_id, data=data)
            )
            return Response().response(status_code=200, message_id="typing_proposal_successful")
        except Exception as e:
            # Loga o erro e retorna uma resposta apropriada
            logdb("error", message=f"Error typing proposal: {e}")
            return Response().response(
                status_code=400,
                error=True,
                message_id="error_typing_proposal",
                exception=str(e)
            )

    def list_proposal(self, data: dict):
        current_page, rows_per_page = int(data.get("current_page", 1)), int(data.get("rows_per_page", 10))

        if current_page < 1:
            current_page = 1
        if rows_per_page < 1:
            rows_per_page = 1

        pagination = Pagination().pagination(current_page=current_page, rows_per_page=rows_per_page, sort_by=data.get("sort_by", ""), order_by=data.get("order_by", ""), filter_by=data.get("filter_by", ""))

        proposal = self.pg.fetch_to_dict(query=self.models.list_proposal(pagination=pagination))

        if not proposal:
            return Response().response(status_code=404, error=True, message_id="proposal_list_not_found", exception="Not found", data=proposal)

        metadata = Pagination().metadata(current_page=current_page, rows_per_page=rows_per_page, sort_by=pagination["sort_by"], order_by=pagination["order_by"], filter_by=pagination["filter_by"])
        return Response().response(status_code=200, message_id="proposal_list_successful", data=proposal, metadata=metadata)

    def count_proposal(self):
        try:
            count = self.pg.fetch_to_dict(query=self.models.count_proposal())
            return Response().response(status_code=200, message_id="count_proposal_successful", data=count)
        except Exception as e:
            logdb("error", message=f"Error Count Proposal: {e}")
            return Response().response(status_code=400, error=True, message_id="error_count_proposal", exception=str(e))

    def history_proposal(self, proposal_id: int, data: dict):
        current_page, rows_per_page = int(data.get("current_page", 1)), int(data.get("rows_per_page", 10))

        if current_page < 1:
            current_page = 1
        if rows_per_page < 1:
            rows_per_page = 1

        pagination = Pagination().pagination(current_page=current_page, rows_per_page=rows_per_page, sort_by=data.get("sort_by", ""), order_by=data.get("order_by", ""), filter_by=data.get("filter_by", ""))

        history = self.pg.fetch_to_dict(query=self.models.history_proposal(pagination=pagination, proposal_id=proposal_id))

        if not history:
            return Response().response(status_code=404, error=True, message_id="history_list_not_found", exception="Not found", data=history)

        metadata = Pagination().metadata(current_page=current_page, rows_per_page=rows_per_page, sort_by=pagination["sort_by"], order_by=pagination["order_by"], filter_by=pagination["filter_by"])
        return Response().response(status_code=200, message_id="history_list_successful", data=history, metadata=metadata)
    
    
    def details_propsal(self, proposal_id):
        try:
            details = self.pg.fetch_to_dict(query=self.models.details_proposal(id=proposal_id))
            
            if not details:
                return Response().response(status_code=404, error=True, message_id="details_list_not_found", exception="Not found", data=details)
                
            return Response().response(status_code=200, message_id="details_proposal_successful", data=details)
        except Exception as e:
            logdb("error", message=f"Error Count Proposal: {e}")
            return Response().response(status_code=400, error=True, message_id="error_count_proposal", exception=str(e))