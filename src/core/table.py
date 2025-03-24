import os
from pandas import read_excel
from src.models.table import TablesFinanceModels
from src.db.pg import PgAdmin
from src.service.response import Response
from src.utils.pagination import Pagination
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from src.utils.log import logdb

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "upload")

class TablesFinanceCore:

    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.pg = PgAdmin()
        self.models = TablesFinanceModels(user_id=user_id)

    def rank_comission(self, data: dict) -> None:
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
        
        rank = self.pg.fetch_to_dict(query=self.models.rank_comission(pagination=pagination))
        
        metadata = Pagination().metadata(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=pagination["sort_by"],
            order_by=pagination["order_by"],
            filter_by=pagination["filter_by"],
        )

        return Response().response(status_code=200, error=False, message_id="list_rank_successful", data=rank, metadata=metadata)

    def add_table(self, data: dict) -> None:
        try:
            if not data.get("financial_agreements_id"):
                return Response().response(status_code=400, error=True, message_id="financial_agreements_id")

            self.pg.execute_query(query=self.models.add_tables(data=data))
            self.pg.commit()
            return Response().response(status_code=200, error=False, message_id="tables_add_sucessfull")
        except Exception as e:
            logdb("error", message=f"Error processing add tables: {e}")
            return Response().response(status_code=500, error=True, message_id="error_add_tables", exception=str(e))

    def add_tables_finance(self, data: dict, file: FileStorage) -> None:
        try:
            if not file or file.filename == '':
                return Response().response(status_code=400, error=False, message_id="is_required_xlsx")

            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)

            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            dftmp = read_excel(filepath, dtype="object", engine="openpyxl")
            dftmp = dftmp.fillna("")
            for index, row in dftmp.iterrows():
                self.pg.execute_query(query=self.models.add_tables_finance(
                    data={
                    "name": row['Tabela'],
                    "type_table": row['Tipo'],
                    "table_code": row['Cod Tabela'],
                    "start_term": row['Prazo Inicio'],
                    "end_term": row['Prazo Fim'],
                    "rate": row['Flat'],
                    "start_rate": row['Taxa Inicio'],
                    "end_rate": row['Taxa Fim'],
                    },
                    financial_agreements_id=data.get("financialagreements_id"),
                    issue_date=data.get("issue_date"),
                ))

            self.pg.commit()
            os.remove(filepath)
            return Response().response(status_code=200, error=False, message_id="tables_import_successfull", metadata={"file": filename})
        except FileNotFoundError as fnf_err:
            os.remove(filepath)
            logdb("error", message=f"Erro processing tables:  {e}")
            return Response().response(status_code=400, error=True, message_id="xlsx_is_not_save", exception=str(fnf_err))
        except KeyError as key_err:
            os.remove(filepath)
            logdb("error", message=f"Erro processing tables:  {e}")
            return Response().response(status_code=400, error=True, message_id="excel_with_missing_rows_or_columns", exception=str(key_err))
        except Exception as e:
            logdb("error", message=f"Erro processing tables:  {e}")
            return Response().response(status_code=400, error=True, message_id="error_processing_xlsx", exception=str(e))

    def list_board_table(self, data: dict, financial_agreements_id: int) -> None:
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

        board_table = self.pg.fetch_to_dict(query=self.models.list_board_tables(pagination=pagination, financial_agreements=financial_agreements_id))
        
        if not board_table:
            return Response().response(status_code=404, error=True, message_id="board_table_not_found", exception="Not found", data=board_table)

        metadata = Pagination().metadata(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=pagination["sort_by"],
            order_by=pagination["order_by"],
            filter_by=pagination["filter_by"],
        )

        return Response().response(status_code=200, error=False, message_id="list_board_tables_successful", data=board_table, metadata=metadata)

    def delete_tabels_ids(self, id: int, data: dict) -> None:
        try:
            tables_ids = self.pg.execute_query(query=self.models.delete_tables_ids(ids=data.get("ids"), financial_agreements_id=id))
            return Response().response(status_code=200, error=False, message_id="delete_table_ids_successful", data=tables_ids)
        except Exception as e:
            logdb("error", message=f"Erro processing tables:  {e}")