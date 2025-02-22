import os
import io
import traceback
from pandas import DataFrame
from pandas import read_excel, read_csv
from src.models.reportfinance import ReportModels
from src.db.pg import PgAdmin
from src.service.response import Response
from src.utils.pagination import Pagination
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from openpyxl import Workbook
from src.utils.log import setup_logger
from psycopg2.errors import UniqueViolation
from psycopg2.errors import ForeignKeyViolation

logger = setup_logger(__name__)

dftmp = None
REPORT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "report")


class ReportCore:

    def __init__(self, user_id: int, *args, **kwargs):
        self.pg = PgAdmin()
        self.models = ReportModels(user_id=user_id)

    def add_report(self, data: dict, file: FileStorage) -> None:
        global dftmp
        try:
            required_columns = ['CPF', 'NUMERO_PROPOSTA', 'COD_TAB', 'VALOR_OPERACAO']
            batch_insert = []
            if not file or file.filename == '':
                logger.warning("Is required xlsx or csv.")
                return Response().response(status_code=400, error=True, message_id="is_required_xlsx_or_csv")

            if not os.path.exists(REPORT_FOLDER):
                os.makedirs(REPORT_FOLDER)

            filename = secure_filename(file.filename)
            filepath = os.path.join(REPORT_FOLDER, filename)
            file.save(filepath)

            if filepath.endswith(".xlsx"):
                dftmp = read_excel(filepath, dtype="object", engine="openpyxl")

            elif filepath.endswith(".csv"):
                with open(filepath, 'r') as csv_file:
                    first_line = csv_file.readline()
                    delimiter = ',' if ',' in first_line else ';'
                dftmp = read_csv(filepath, sep=delimiter, dtype="object")
            else:
                logger.warning("Unsupported file format.")
                return Response().response(status_code=400, error=True, message_id="unsupported_file_format")

            if dftmp is None or dftmp.empty:
                logger.warning(f"Empty or invalid file")
                return Response().response(status_code=400, error=True, message_id="empty_or_invalid_file")

            if all(column in dftmp.columns for column in required_columns):
                for index, row in dftmp.iterrows():
                    try:
                        batch_insert.append((data.get('name'), row['CPF'], row['NUMERO_PROPOSTA'], row['COD_TAB'], row['VALOR_OPERACAO'], False))
                    except UniqueViolation as q:
                        logger.warning(f"Name '{data.get('name')}' already exists. Skipping...")
                        return Response().response(status_code=409, error=True, message_id="name_already_exists", exception=str(q))

                self.pg.execute_query(query=self.models.add_report(batch_list=batch_insert))
                self.pg.commit()
                os.remove(filepath)
                return Response().response(status_code=200, message_id="add_report_sucessfull")
            else:
                logger.warning("Missing mandatory columns")
                return Response().response(status_code=409, error=True, message_id="missing_mandatory_columns")

        except FileNotFoundError as fnf_err:
            os.remove(filepath)
            logger.error(f"Xlsx or Csv Is Not Save {fnf_err}", exc_info=True)
            return Response().response(status_code=400, error=True, message_id="xlsx_or_csv_is_not_saved", exception=str(fnf_err))
        except KeyError as key_err:
            os.remove(filepath)
            logger.error(f"Excel With Missing Columns {key_err}", exc_info=True)
            return Response().response(status_code=400, error=True, message_id="excel_with_missing_rows_or_columns", exception=str(key_err))
        except Exception as e:
            os.remove(filepath)
            logger.error(f"Error Processing Xlsx or Csv {e}", exc_info=True)
            return Response().response(status_code=400, error=True, message_id="error_processing_xlsx_or_csv", exception=str(e))

    def processing_payments(self, data: dict):
        try:
            if data.get("decision_maker"):
                decision_maker = self.pg.fetch_to_all(query=self.models.list_decision_maker(ids=data.get("user_id")))
                if not decision_maker:
                    logger.warning("No decision maker")
                    return Response().response(status_code=409, error=True, message_id="no_decision_maker", exception="No decision maker")
                self.pg.execute_query(query=self.models.processing_payment(proposals=decision_maker, data=data, user_ids=decision_maker))
                self.pg.commit()
            else:
                check = self.pg.fetch_to_dict(query=self.models.check_proposal(ids=data.get("user_id")))
                if not check:
                    logger.warning("No paids proposal")
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
            logger.warning(f"List processing payments List Not Found.")
            return Response().response(status_code=404, error=True, message_id="list_processing_list_not_found", exception="Not found", data=list_payments)

        metadata = Pagination().metadata(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=pagination["sort_by"],
            order_by=pagination["order_by"],
            filter_by=pagination["filter_by"],
        )
        return Response().response(status_code=200, message_id="list_payments_successful", data=list_payments, metadata=metadata)

    def export_processing_payments(self, file_type: str) -> None:
        from flask import Response
        try:
            if file_type == "csv":
                result = self.pg.fetch_to_all(query=self.models.export_report())

                if not result:
                    logger.warning(f"No data found for export.")
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
                logger.warning(f"Invalid file type. Only 'csv' or 'xlsx' are supported")
                return Response("Invalid file type. Only 'csv' or 'xlsx' are supported.", status=400, content_type="text/plain")

        except Exception as e:
            logger.error(f"error_processing_xlsx_or_csv {e}", exc_info=True)
            return Response(f"Error: {str(e)}\n{traceback.format_exc()}", status=400, content_type="text/plain")

    def list_import(self, data: dict = {}) -> None:
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
                filter_by=data.get("filter_by", ""),
            )

            list_import = self.pg.fetch_to_dict(query=self.models.list_import(pagination=pagination))
            if not list_import:
                logger.warning(f"List Imports Proposal Not Found.")
                return Response().response(status_code=404, error=True, message_id="list_report_import_not_found", exception="Not found", data=list_import)

            metadata = Pagination().metadata(current_page=current_page, rows_per_page=rows_per_page, sort_by=pagination["sort_by"], order_by=pagination["order_by"], filter_by=pagination["filter_by"])
            return Response().response(status_code=200, message_id="list_report_import_successful", data=list_import, metadata=metadata)
        except Exception as e:
            logger.error(f"Error Imports report proposal. {e}", exc_info=True)
            return Response().response(status_code=400, error=True, message_id="error_list_import_proposal", exception=str(e), traceback=traceback.format_exc(e))

    def list_flags(self, data: dict) -> None:
        try:
            current_page, rows_per_page = int(data.get("current_page", 1)), int(data.get("rows_per_page", 10))

            if current_page < 1:  # Force variables min values
                current_page = 1
            if rows_per_page < 1:
                rows_per_page = 1

            pagination = Pagination().pagination(current_page=current_page, rows_per_page=rows_per_page, sort_by=data.get("sort_by", ""), order_by=data.get("order_by", ""), filter_by=data.get("filter_by", ""))

            flags = self.pg.fetch_to_dict(query=self.models.list_flags(pagination=pagination))

            if not flags:
                logger.warning(f"Flags not Found.")
                return Response().response(status_code=404, error=True, message_id="flags_not_found", exception="Not found", data=flags)

            metadata = Pagination().metadata(current_page=current_page, rows_per_page=rows_per_page, sort_by=pagination["sort_by"], order_by=pagination["order_by"], filter_by=pagination["filter_by"])
            return Response().response(status_code=200, message_id="flags_successful", data=flags, metadata=metadata)
        except Exception as e:
            logger.error(f"Error check report proposal. {e}", exc_info=True)
            return Response().response(status_code=400, error=True, message_id="error_check_report_proposal", exception=str(e), traceback=traceback.format_exc(e))

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
                logger.warning(f"Sellers not Found.")
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
            logger.error(f"Error check report proposal. {e}", exc_info=True)
            return Response().response(status_code=400, error=True, message_id="error_check_report_proposal", exception=str(e), traceback=traceback.format_exc(e))

    def add_flags(self, data: dict):
        try:
            if not data.get("name"):
                logger.warning("Name is required")
                return Response().response(status_code=400, error=True, message_id="name_is_required", exception="Name is required")

            self.pg.execute_query(query=self.models.add_flag(data=data))
            self.pg.commit()
            return Response().response(status_code=200, error=False, message_id="add_flags_successfully")
        except UniqueViolation:
            return Response().response(status_code=409, error=True, message_id="name_already_exists")
        except Exception as e:
            print(e)
            return Response().response(status_code=400, error=True, message_id="erro_processing", exception=str(e))

    def delete_flag(self, data: dict):
        try:
            if not data.get("ids"):
                logger.warning("Ids is required")
                return Response().response(status_code=400, error=True, message_id="id_is_required", exception="Ids is required")

            self.pg.execute_query(query=self.models.delete_flag(ids=data.get("ids")))
            self.pg.commit()
            return Response().response(status_code=200, error=False, message_id="delete_flags_successfully")
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="erro_processing", exception=str(e))

    def delete_imports(self, name: str):
        try:
            self.pg.execute_query(query=self.models.delete_import(name=name))
            self.pg.commit()
            return Response().response(status_code=200, error=False, message_id="delete_report_import_successfully")
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="erro_processing", exception=str(e))

    def delete_processing_payment(self, data: dict):
        try:
            if not data.get("ids"):
                return Response().response(status_code=409, error=True, message_id="ids_is_required", exception="IDS is required")
            self.pg.execute_query(query=self.models.delete_processing_payment(ids=data.get("ids")))
            self.pg.commit()
            return Response().response(status_code=200, error=False, message_id="delete_processing_payments_successfully")
        except Exception as e:
            return Response().response(status_code=500, error=False, message_id="erro_processing_delete_payments",)