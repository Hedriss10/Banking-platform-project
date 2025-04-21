import io
import traceback

from openpyxl import Workbook
from pandas import DataFrame
from psycopg2.errors import ForeignKeyViolation, UniqueViolation

from src.db.pg import PgAdmin
from src.models.payment import PayamentsModels
from src.service.response import Response
from src.utils.log import logdb
from src.utils.pagination import Pagination


class PaymentsCore:
    
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.pg = PgAdmin()
        self.models = PayamentsModels(user_id=user_id)

    def processing_payments(self, data: dict):
        try:
            if data.get("decision_maker") == True:
                decision_maker = self.pg.fetch_to_all(query=self.models.list_decision_maker(ids=data.get("user_id")))
                
                if not decision_maker:
                    return Response().response(status_code=409, error=True, message_id="no_decision_maker", exception="No decision maker")
                
                self.pg.execute_query(query=self.models.processing_payment(proposals=decision_maker, data=data, user_ids=decision_maker))
                self.pg.commit()
            else:
                check = self.pg.fetch_to_dict(query=self.models.check_proposal(ids=data.get("user_id")))
                if not check:
                    return Response().response(status_code=409, error=True, message_id="no_paid_proposals", exception="No paid proposal")

                self.pg.execute_query(query=self.models.report_validated(number_proposal=check))
                self.pg.execute_query(query=self.models.processing_payment(proposals=check, data=data, user_ids=check))
                self.pg.commit()

            return Response().response(status_code=200, error=False, message_id="payments_process_successfull")
        except ForeignKeyViolation as fk:
            return Response().response(status_code=409, error=True, message_id="flag_or_user_is_not_present_database", exception=str(fk))
        except UniqueViolation as q:
            return Response().response(status_code=409, error=True, message_id="duplicate_proposal_processing_payments", exception=str(q))
        except Exception as e:
            return Response().response(status_code=417, error=True, message_id="error_processing_payment", exception=str(e))
        
    def list_processing_payments(self, data: dict = {}) -> None:
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

        list_payments = self.pg.fetch_to_dict(query=self.models.list_processing_payments(pagination=pagination))

        if not list_payments:
            return Response().response(status_code=404, error=True, message_id="list_processing_list_not_found", exception="Not found", data=list_payments)

        metadata = Pagination().metadata(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=pagination["sort_by"],
            order_by=pagination["order_by"],
            filter_by=pagination["filter_by"],
        )
        return Response().response(status_code=200, message_id="list_payments_successful", data=list_payments, metadata=metadata)
    
    def list_sellers(self, data: dict) -> None:
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
            )

            sellers = self.pg.fetch_to_dict(query=self.models.list_sellers(name_report=data.get("name_report"), has_report=data.get("has_report"), pagination=pagination))
            
            if not sellers:
                return Response().response(status_code=404, error=True, message_id="sellers_not_found", exception="Not found", data=sellers)

            metadata = Pagination().metadata(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=pagination["sort_by"],
                order_by=pagination["order_by"],
                filter_by=pagination["filter_by"],
            )
            return Response().response(status_code=200, message_id="sellers_successful", data=sellers, metadata=metadata)
        except Exception as e:
            logdb("error", message=f"Error check report proposal. {e}")
            return Response().response(status_code=400, error=True, message_id="error_check_report_proposal", exception=str(e), traceback=traceback.format_exc(e))
    
    def delete_processing_payment(self, data: dict):
        try:
            if not data.get("ids"):
                return Response().response(status_code=409, error=True, message_id="ids_is_required", exception="IDS is required")
            
            self.pg.execute_query(query=self.models.delete_processing_payment(ids=data.get("ids")))
            self.pg.commit()
            return Response().response(status_code=200, error=False, message_id="delete_processing_payments_successfully")
        except Exception as e:
            return Response().response(status_code=500, error=False, message_id="erro_processing_delete_payments",)
    
    def export_processing_payments(self, file_type: str) -> None:
        from flask import Response
        try:
            if file_type == "csv":
                result = self.pg.fetch_to_all(query=self.models.export_report())

                if not result:
                    return Response("No data found for export.", status=404, content_type="text/plain")

                df = DataFrame(result)
                df.rename(columns={"cpf_client": "CPF", "user_name_seller": "Nome do Vendedor", "number_proposal": "Número da Proposta", "value_operation": "Valor Da Operação", "taxe_comission": "Taxa De Comissão", "value_base": "Valor Base", "taxe_repasse": "Taxa Repassada", "comission": "Comissão", "table_code": "Código de Tabela"}, inplace=True)

                output = io.StringIO()
                df.to_csv(output, index=False, sep=";")
                output.seek(0)

                return Response(output.getvalue(), status=200, content_type="text/csv", headers={"Content-Disposition": "attachment; filename=processing_payments.csv"})

            elif file_type == "xlsx":
                result = self.pg.fetch_to_all(query=self.models.export_report())
                if not result:
                    return Response("No data found for export.", status=404, content_type="text/plain")

                df = DataFrame(result)
                df.rename(columns={"cpf_client": "CPF", "user_name_seller": "Nome do Vendedor", "number_proposal": "Número da Proposta", "value_operation": "Valor Da Operação", "taxe_comission": "Taxa De Comissão", "value_base": "Valor Base", "taxe_repasse": "Taxa Repassada", "comission": "Comissão", "table_code": "Código de Tabela"}, inplace=True)

                output = io.BytesIO()
                writer = Workbook()

                sheet = writer.active
                sheet.title = "Sheet1"
                sheet.append(df.columns.tolist())
                for i, row in df.iterrows():
                    sheet.append(row.tolist())

                writer.save(output)
                output.seek(0)

                return Response(output.getvalue(), status=200, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=processing_payments.xlsx"})

            else:
                logdb("warning", message=f"Invalid file type. Only 'csv' or 'xlsx' are supported")
                return Response("Invalid file type. Only 'csv' or 'xlsx' are supported.", status=400, content_type="text/plain")

        except Exception as e:
            logdb("error", message=f"Error processing xlsx or csv: {e}")
            return Response(f"Error: {str(e)}\n{traceback.format_exc()}", status=400, content_type="text/plain")


class Payments:
    
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id

