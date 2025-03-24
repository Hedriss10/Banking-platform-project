import os
import traceback

from pandas import read_excel, read_csv
from src.models.report import ReportModels
from src.db.pg import PgAdmin
from src.service.response import Response
from src.utils.pagination import Pagination
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from src.utils.log import logdb
from psycopg2.errors import UniqueViolation

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
                logdb("warning", message="Unsupported file format.")
                return Response().response(status_code=400, error=True, message_id="unsupported_file_format")

            if dftmp is None or dftmp.empty:
                logdb("warning", message="Empty or invalid file.")
                return Response().response(status_code=400, error=True, message_id="empty_or_invalid_file")

            if all(column in dftmp.columns for column in required_columns):
                for index, row in dftmp.iterrows():
                    try:
                        batch_insert.append((data.get('name'), row['CPF'], row['NUMERO_PROPOSTA'], row['COD_TAB'], row['VALOR_OPERACAO'], False))
                    except UniqueViolation as q:
                        logdb("warning", message=f"Name '{data.get('name')}' already exists. Skipping...")
                        return Response().response(status_code=409, error=True, message_id="name_already_exists", exception=str(q))

                self.pg.execute_query(query=self.models.add_report(batch_list=batch_insert))
                self.pg.commit()
                os.remove(filepath)
                return Response().response(status_code=200, message_id="add_report_sucessfull")
            else:
                logdb("warning", message="Missing mandatory columns.")
                return Response().response(status_code=409, error=True, message_id="missing_mandatory_columns")

        except FileNotFoundError as fnf_err:
            os.remove(filepath)
            logdb("error", message=f"Xlsx or Csv Is Not Save {fnf_err}")
            return Response().response(status_code=400, error=True, message_id="xlsx_or_csv_is_not_saved", exception=str(fnf_err))
        except KeyError as key_err:
            os.remove(filepath)
            logdb("error", message=f"Excel With Missing Columns {key_err}")
            return Response().response(status_code=400, error=True, message_id="excel_with_missing_rows_or_columns", exception=str(key_err))
        except Exception as e:
            os.remove(filepath)
            logdb("error", message=f"Error Processing Xlsx or Csv {e}")
            return Response().response(status_code=400, error=True, message_id="error_processing_xlsx_or_csv", exception=str(e))

    def list_import(self, data: dict) -> None:
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
                return Response().response(status_code=404, error=True, message_id="list_report_import_not_found", exception="Not found", data=list_import)

            metadata = Pagination().metadata(current_page=current_page, rows_per_page=rows_per_page, sort_by=pagination["sort_by"], order_by=pagination["order_by"], filter_by=pagination["filter_by"])
            return Response().response(status_code=200, message_id="list_report_import_successful", data=list_import, metadata=metadata)
        except Exception as e:
            logdb("error", message=f"Error Imports report proposal. {e}")
            return Response().response(status_code=400, error=True, message_id="error_list_import_proposal", exception=str(e), traceback=traceback.format_exc(e))

    def delete_imports(self, name: str):
        try:
            self.pg.execute_query(query=self.models.delete_import(name=name))
            self.pg.commit()
            return Response().response(status_code=200, error=False, message_id="delete_report_import_successfully")
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="erro_processing", exception=str(e))
