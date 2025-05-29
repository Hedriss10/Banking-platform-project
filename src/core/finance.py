# src/core/bankers.py

import os
from datetime import datetime

from pandas import read_csv, read_excel
from sqlalchemy import and_, func, insert, or_, select, update
from sqlalchemy.exc import IntegrityError
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from src.db.database import db
from src.models.models import (
    Bankers,
    FinancialAgreements,
    ObtianReport,
    TablesFinance,
    User,
)
from src.service.response import Response
from src.utils.log import logdb
from src.utils.metadata import Metadata
from src.utils.pagination import Pagination

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ),
    "upload",
)
REPORT_FOLDER = os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ),
    "report",
)


class BankersCore:
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        self.bankers = Bankers
        self.financial_agreements = FinancialAgreements

    def list_bankers(self, data: dict) -> None:
        try:
            current_page = int(data.get("current_page", 1))
            rows_per_page = int(data.get("rows_per_page", 10))

            current_page = max(current_page, 1)
            rows_per_page = max(rows_per_page, 1)

            pagination = Pagination().pagination(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=data.get("sort_by", ""),
                order_by=data.get("order_by", ""),
                filter_by=data.get("filter_by", ""),
                filter_value=data.get("filter_value", ""),
            )

            stmt = select(
                self.bankers.id,
                self.bankers.name,
                func.to_char(self.bankers.created_at, "YYYY-MM-DD").label(
                    "created_at"
                ),
            ).where(self.bankers.is_deleted == False)

            # Filtro dinâmico
            if pagination["filter_value"]:
                filter_value = f"%{pagination['filter_value']}%"
                stmt = stmt.where(
                    or_(
                        func.unaccent(self.bankers.name).ilike(
                            func.unaccent(filter_value)
                        )
                    )
                )

            if pagination["order_by"]:
                sort_column = getattr(
                    self.bankers, pagination["order_by"], None
                )
                if sort_column is not None:
                    if pagination["sort_by"] == "asc":
                        stmt = stmt.order_by(sort_column.asc())
                    else:
                        stmt = stmt.order_by(sort_column.desc())
            else:
                stmt = stmt.order_by(self.bankers.id.desc())

            # Aplicar paginação
            paginated_stmt = stmt.offset(pagination["offset"]).limit(
                pagination["limit"]
            )
            result = db.session.execute(paginated_stmt).fetchall()

            if not result:
                return Response().response(
                    status_code=404,
                    error=True,
                    message_id="bankers_list_not_found",
                    exception="Not found",
                )

            # Total respeitando o filtro
            count_stmt = select(func.count()).select_from(
                select(self.bankers.id)
                .where(self.bankers.is_deleted == False)
                .where(
                    or_(
                        func.unaccent(self.bankers.name).ilike(
                            func.unaccent(filter_value)
                        )
                    )
                    if pagination["filter_value"]
                    else True
                )
                .subquery()
            )
            total = db.session.execute(count_stmt).scalar()

            metadata = Pagination().metadata(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=pagination["sort_by"],
                order_by=pagination["order_by"],
                filter_by=pagination["filter_by"],
                filter_value=pagination["filter_value"],
                total=total,
            )

            return Response().response(
                status_code=200,
                message_id="bankers_list_bankers_successful",
                error=False,
                data=Metadata(result).model_to_list(),
                metadata=metadata,
            )
        except Exception as e:
            logdb("error", message=f"Error List Bankers: {str(e)}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="bankers_list_error",
                exception=str(e),
            )

    def get_banker(self, id: int) -> None:
        try:
            stmt = (
                select(
                    self.bankers.id.label("bank_id"),
                    func.initcap(func.trim(self.bankers.name)).label(
                        "bank_name"
                    ),
                    func.to_char(self.bankers.created_at, "YYYY-MM-DD").label(
                        "created_at"
                    ),
                    func.json_agg(
                        func.json_build_object(
                            "id_financialagreements",
                            self.financial_agreements.id,
                            "financialagreements_name",
                            func.initcap(
                                func.trim(self.financial_agreements.name)
                            ),
                        )
                    ).label("financial_agreements"),
                )
                .where(
                    self.bankers.is_deleted == False,
                    self.bankers.id == id,
                )
                .join(
                    self.financial_agreements,
                    and_(
                        self.bankers.id == self.financial_agreements.banker_id,
                        self.financial_agreements.is_deleted == False,
                    ),
                )
                .group_by(self.bankers.id, self.bankers.name)
            )

            result = db.session.execute(stmt).fetchall()

            if not result:
                return Response().response(
                    status_code=404,
                    error=True,
                    message_id="banker_not_found",
                    exception="Not found",
                )

            return Response().response(
                status_code=200,
                error=False,
                message_id="banker_get_successful",
                data=Metadata(result).model_to_list(),
            )

        except Exception as e:
            logdb("error", message=f"Error Get Banker, {e}")
            return Response().response(
                status_code=500, error=True, message_id="banker_get_error"
            )

    def add_banker(self, data: dict) -> None:
        try:
            if not data.get("name"):
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="banker_name_is_required",
                    exception="Banker Name Is Required",
                )

            bankers = (
                insert(self.bankers)
                .values(name=data.get("name"), created_at=datetime.now())
                .returning(self.bankers.id)
            )
            bankers = db.session.execute(bankers).scalar()
            db.session.commit()

            return Response().response(
                status_code=200,
                error=False,
                message_id="banker_register_successful",
            )
        except IntegrityError:
            db.session.rollback()
            logdb("warning", "Name already exists")
            return Response().response(
                status_code=400,
                message_id="name_bankers_already_exists",
                error=True,
                exception="Name already exists",
            )
        except Exception as e:
            db.session.rollback()
            logdb("error", message=f"Error Add Bankers, {e}")
            return Response().response(
                status_code=500, error=True, message_id="bankers_add_error"
            )

    def update_banker(self, id: int, data: dict) -> None:
        try:
            if not data.get("name"):
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="banker_name_is_required",
                    exception="Banker Name Is Required",
                )

            bankers = (
                update(self.bankers)
                .where(self.bankers.id == id)
                .values(
                    name=data.get("name"),
                    updated_at=datetime.now(),
                    updated_by=self.user_id,
                )
                .returning(self.bankers.id)
            )

            bankers = db.session.execute(bankers).scalar()
            db.session.commit()

            return Response().response(
                status_code=200,
                error=False,
                message_id="banker_update_successful",
            )

        except Exception as e:
            logdb("error", message=f"Error Update Bankers, {e}")
            return Response().response(
                status_code=500, error=True, message_id="bankers_update_error"
            )

    def delete_banker(self, id: int) -> None:
        try:
            if not id:
                return Response().response(
                    status_code=401,
                    error=True,
                    message_id="banker_name_id_is_required",
                    exception="Banker Id Is Required",
                )

            bankers = (
                update(self.bankers)
                .where(self.bankers.id == id)
                .values(is_deleted=True)
                .returning(self.bankers.id)
            )
            bankers = db.session.execute(bankers).scalar()
            db.session.commit()

            return Response().response(
                status_code=200,
                error=False,
                message_id="banker_delete_successful",
            )
        except Exception as e:
            logdb("error", message=f"Error Delete Bankers, {e}")
            return Response().response(
                status_code=500, error=True, message_id="bankers_update_error"
            )


class FinancialAgreementsCore:
    def __init__(self, user_id: int, *args, **kwargs) -> None:
        self.user_id = user_id
        self.financial_agreements = FinancialAgreements

    def add_financial_agreements(self, data: dict) -> None:
        try:
            if not data.get("name"):
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="financial_agreements_is_required",
                    exception="Financial Agreements Name Is Required",
                )

            financial_agreements = (
                insert(self.financial_agreements)
                .values(
                    name=data.get("name"),
                    banker_id=data.get("banker_id"),
                    created_at=datetime.now(),
                )
                .returning(self.financial_agreements.id)
            )
            financial_agreements = db.session.execute(
                financial_agreements
            ).scalar()
            db.session.commit()

            return Response().response(
                status_code=200,
                error=False,
                message_id="financial_agreements_register_successful",
            )

        except Exception as e:
            logdb("error", message=f"Error Adds financial agreements, {e}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="financial_agreements_add_error",
            )

    def update_financial_agreements(self, id: int, data: dict) -> None:
        try:
            if not data.get("name"):
                return Response().response(
                    status_code=401,
                    error=True,
                    message_id="financial_agreements_name_is_required",
                    exception="Financial Agreements Name Is Required",
                )

            financial_agreements = (
                update(self.financial_agreements)
                .where(self.financial_agreements.id == id)
                .values(
                    name=data.get("name"),
                    updated_at=datetime.now(),
                    updated_by=self.user_id,
                )
                .returning(self.financial_agreements.id)
            )
            financial_agreements = db.session.execute(
                financial_agreements
            ).scalar()
            db.session.commit()

            return Response().response(
                status_code=200,
                error=False,
                message_id="financial_agreements_update_successful",
            )

        except Exception as e:
            logdb("error", message=f"Error Edit financial agreements, {e}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="financial_agreements_edit_error",
            )

    def delete_financial_agreements(self, id: int) -> None:
        try:
            if not id:
                return Response().response(
                    status_code=401,
                    error=True,
                    message_id="financial_agreements_is_required",
                    exception="Financial Agreements Id Is Required",
                )

            financial_agreements = (
                update(self.financial_agreements)
                .where(self.financial_agreements.id == id)
                .values(
                    is_deleted=True,
                    deleted_at=datetime.now(),
                    deleted_by=self.user_id,
                )
                .returning(self.financial_agreements.id)
            )

            financial_agreements = db.session.execute(
                financial_agreements
            ).scalar()
            db.session.commit()

            return Response().response(
                status_code=200,
                error=False,
                message_id="financial_agreements_delete_successful",
            )
        except Exception as e:
            logdb("error", message=f"Error Delete financial agreements, {e}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="financial_agreements_delete_error",
            )


class TablesCore:
    def __init__(self, user_id: int, *args, **kwargs) -> None:
        self.user_id = user_id
        self.tables = TablesFinance
        self.bankers = Bankers
        self.financial_agreements = FinancialAgreements

    def rank_comission(self, data: dict) -> None:
        try:
            current_page, rows_per_page = (
                int(data.get("current_page", 1)),
                int(data.get("rows_per_page", 10)),
            )
            current_page = max(current_page, 1)
            rows_per_page = max(rows_per_page, 1)

            pagination = Pagination().pagination(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=data.get("sort_by", ""),
                order_by=data.get("order_by", ""),
                filter_by=data.get("filter_by", ""),
                filter_value=data.get("filter_value", ""),
            )

            stmt = (
                select(
                    self.tables.id,
                    self.tables.name.label("table"),
                    func.trim(self.bankers.name).label("name_banker"),
                    self.tables.table_code,
                    self.tables.rate,
                    self.tables.start_rate,
                    self.tables.end_rate,
                )
                .join(
                    self.financial_agreements,
                    self.financial_agreements.id
                    == self.tables.financial_agreements_id,
                )
                .join(
                    self.bankers,
                    self.bankers.id == self.financial_agreements.banker_id,
                )
                .where(
                    self.tables.is_deleted.is_(False),
                    self.financial_agreements.is_deleted.is_(False),
                    self.bankers.is_deleted.is_(False),
                )
                .group_by(
                    self.tables.id,
                    self.bankers.id,
                    self.financial_agreements.id,
                )
                .order_by(self.tables.rate.desc())
            )

            # Filtro dinâmico
            if pagination["filter_value"]:
                filter_value = f"%{pagination['filter_value']}%"
                stmt = stmt.where(
                    or_(
                        func.unaccent(self.tables.name).ilike(
                            func.unaccent(filter_value)
                        ),
                        func.unaccent(self.tables.table_code).ilike(
                            func.unaccent(filter_value)
                        ),
                    )
                )

            if pagination["order_by"]:
                sort_column = getattr(
                    self.tables, pagination["order_by"], None
                )
                if sort_column is not None:
                    if pagination["sort_by"] == "asc":
                        stmt = stmt.order_by(sort_column.asc())
                    else:
                        stmt = stmt.order_by(sort_column.desc())
            else:
                stmt = stmt.order_by(self.bankers.id.desc())

            # Aplicar paginação
            paginated_stmt = stmt.offset(pagination["offset"]).limit(
                pagination["limit"]
            )
            result = db.session.execute(paginated_stmt).fetchall()

            # Total respeitando o filtro
            count_stmt = select(func.count()).select_from(
                select(self.bankers.id)
                .where(self.bankers.is_deleted == False)
                .where(
                    or_(
                        func.unaccent(self.tables.table_code).ilike(
                            func.unaccent(filter_value)
                        )
                    )
                    if pagination["filter_value"]
                    else True
                )
                .subquery()
            )
            total = db.session.execute(count_stmt).scalar()
            if not result:
                return Response().response(
                    status_code=404, error=False, message_id="tables_not_found"
                )

            metadata = Pagination().metadata(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=pagination["sort_by"],
                order_by=pagination["order_by"],
                filter_by=pagination["filter_by"],
                total=total,
            )

            return Response().response(
                status_code=200,
                error=False,
                message_id="tables_list",
                data=Metadata(result).model_to_list(),
                metadata=metadata,
            )

        except Exception as e:
            logdb("error", message=f"Error processing add tables: {e}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_add_tables",
                exception=str(e),
            )

    def add_table(self, data: dict) -> None:
        try:
            if not data.get("financial_agreements_id"):
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="financial_agreements_id",
                )

            stmt = insert(self.tables).values(
                name=data.get("name"),
                table_code=data.get("table_code"),
                rate=data.get("rate"),
                start_rate=data.get("start_rate"),
                end_rate=data.get("end_rate"),
                type_table=data.get("type_table"),
                start_term=data.get("start_term"),
                end_term=data.get("end_term"),
                financial_agreements_id=data.get("financial_agreements_id"),
            )
            db.session.execute(stmt)
            db.session.commit()
            return Response().response(
                status_code=200,
                error=False,
                message_id="tables_add_successful",
            )

        except Exception as e:
            logdb("error", message=f"Error processing add tables: {e}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_add_tables",
                exception=str(e),
            )

    def add_tables_import(self, data: dict, file: FileStorage) -> None:
        filepath = None
        try:
            if not file or file.filename == "":
                return Response().response(
                    status_code=400, error=True, message_id="is_required_xlsx"
                )

            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)

            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            # Leitura do arquivo
            dftmp = read_excel(
                filepath, dtype="object", engine="openpyxl"
            ).fillna("")

            if dftmp.empty:
                return Response().response(
                    status_code=400, error=True, message_id="empty_excel_file"
                )

            required_columns = [
                "Tabela",
                "Tipo",
                "Cod Tabela",
                "Prazo Inicio",
                "Prazo Fim",
                "Flat",
                "Taxa Inicio",
                "Taxa Fim",
            ]

            if not all(col in dftmp.columns for col in required_columns):
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="excel_with_missing_rows_or_columns",
                )

            records = []
            for _, row in dftmp.iterrows():
                records.append(
                    {
                        "name": row["Tabela"],
                        "type_table": row["Tipo"],
                        "table_code": row["Cod Tabela"],
                        "start_term": row["Prazo Inicio"],
                        "end_term": row["Prazo Fim"],
                        "rate": row["Flat"],
                        "start_rate": row["Taxa Inicio"],
                        "end_rate": row["Taxa Fim"],
                        "financial_agreements_id": data.get(
                            "financialagreements_id"
                        ),
                        "issue_date": data.get("issue_date"),
                        "created_at": datetime.now(),
                    }
                )

            if not records:
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="no_records_to_insert",
                )

            db.session.bulk_insert_mappings(self.tables, records)
            db.session.commit()

            os.remove(filepath)
            return Response().response(
                status_code=200,
                error=False,
                message_id="tables_import_successful",
            )

        except (FileNotFoundError, KeyError) as e:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
            logdb("error", message=f"Error processing tables: {e}")
            return Response().response(
                status_code=400,
                error=True,
                message_id="xlsx_processing_error",
                exception=str(e),
            )
        except Exception as e:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
            logdb("error", message=f"Error processing tables: {e}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="internal_error_processing_xlsx",
                exception=str(e),
            )

    def list_board_table(
        self, data: dict, financial_agreements_id: int
    ) -> None:
        try:
            current_page, rows_per_page = (
                int(data.get("current_page", 1)),
                int(data.get("rows_per_page", 10)),
            )

            current_page = max(current_page, 1)
            rows_per_page = max(rows_per_page, 1)

            pagination = Pagination().pagination(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=data.get("sort_by", ""),
                order_by=data.get("order_by", ""),
                filter_by=data.get("filter_by", ""),
                filter_value=data.get("filter_value", ""),
            )

            stmt = (
                select(
                    self.tables.id,
                    self.tables.name,
                    self.tables.table_code,
                    self.tables.rate,
                    self.tables.start_rate,
                    self.tables.end_rate,
                    self.tables.type_table,
                    self.tables.start_term,
                    self.tables.end_term,
                )
                .where(
                    self.tables.is_deleted.is_(False),
                    self.tables.financial_agreements_id
                    == financial_agreements_id,
                )
                .group_by(
                    self.tables.id,
                )
            )

            # Filtro dinâmico
            if pagination["filter_value"]:
                filter_value = f"%{pagination['filter_value']}%"
                stmt = stmt.where(
                    or_(
                        func.unaccent(self.tables.name).ilike(
                            func.unaccent(filter_value)
                        ),
                        func.unaccent(self.tables.table_code).ilike(
                            func.unaccent(filter_value)
                        ),
                    )
                )
            if pagination["order_by"]:
                sort_column = getattr(
                    self.tables, pagination["order_by"], None
                )
                if sort_column is not None:
                    if pagination["sort_by"] == "asc":
                        stmt = stmt.order_by(sort_column.asc())
                    else:
                        stmt = stmt.order_by(sort_column.desc())
            else:
                stmt = stmt.order_by(self.tables.id.desc())

            paginated_stmt = stmt.offset(pagination["offset"]).limit(
                pagination["limit"]
            )
            result = db.session.execute(paginated_stmt).fetchall()

            count_stmt = select(func.count()).select_from(
                select(self.tables.id)
                .where(self.tables.is_deleted == False)
                .where(
                    or_(
                        func.unaccent(self.tables.table_code).ilike(
                            func.unaccent(filter_value)
                        )
                    )
                    if pagination["filter_value"]
                    else True
                )
                .subquery()
            )

            total = db.session.execute(count_stmt).scalar()
            if not result:
                return Response().response(
                    status_code=404, error=False, message_id="tables_not_found"
                )

            metadata = Pagination().metadata(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=data.get("sort_by", ""),
                order_by=data.get("order_by", ""),
                filter_by=data.get("filter_by", ""),
                filter_value=data.get("filter_value", ""),
                total=total,
            )

            return Response().response(
                status_code=200,
                error=False,
                message_id="list_board_tables_successful",
                data=Metadata(result).model_to_list(),
                metadata=metadata,
            )

        except Exception as e:
            logdb("error", message=f"Error processing add tables: {e}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_add_tables",
                exception=str(e),
            )

    def delete_tables_ids(self, id: int, data: dict) -> None:
        try:
            ids = data.get("ids", [])

            if not ids:
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="tables_delete_no_ids",
                    exception="No IDs provided",
                )

            stmt = (
                update(self.tables)
                .where(
                    self.tables.financial_agreements_id == id,
                    self.tables.id.in_(ids),
                )
                .values(
                    is_deleted=True,
                    deleted_at=datetime.now(),  # Se quiser com timezone, melhor usar datetime.now(timezone.utc)
                    deleted_by=self.user_id,
                )
            )

            db.session.execute(stmt)
            db.session.commit()

            return Response().response(
                status_code=200,
                error=False,
                message_id="tables_delete_successful",
            )

        except Exception as e:
            logdb("error", message=f"Error deleting tables in batch: {e}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_delete_tables",
                exception=str(e),
            )


class ReportCore:
    # TODO - criar um check summary reports vindo do relatorio
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.report = ObtianReport
        self.user = User

    def add_report(self, data: dict, file: FileStorage) -> None:
        try:
            required_columns = [
                "CPF",
                "NOME",
                "FLAT",
                "BONUS",
                "NUMERO_PROPOSTA",
                "VALOR_OPERACAO",
            ]

            if not file or file.filename == "":
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="report_add_no_file",
                    exception="No file provided",
                )

            if not os.path.exists(REPORT_FOLDER):
                os.mkdir(REPORT_FOLDER)

            filename = secure_filename(file.filename)
            filepath = os.path.join(REPORT_FOLDER, filename)
            file.save(filepath)

            if filepath.endswith(".xlsx"):
                dftmp = read_excel(filepath, dtype="object", engine="openpyxl")

            elif filepath.endswith(".csv"):
                with open(filepath, "r") as csv_file:
                    first_line = csv_file.readline()
                    delimiter = "," if "," in first_line else ";"
                dftmp = read_csv(filepath, sep=delimiter, dtype="object")
            else:
                logdb("warning", message="Unsupported file format.")
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="report_add_unsupported_file_format",
                    exception="Unsupported file format",
                )

            if dftmp is None or dftmp.empty:
                logdb("warning", message="Empty or invalid file.")
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="report_add_empty_or_invalid_file",
                    exception="Empty or invalid file",
                )

            if not all(
                required_columns in dftmp.columns
                for required_columns in required_columns
            ):
                logdb(
                    "warning",
                    message=f"Missing required columns. {data.get('name')}",
                )
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="report_add_required_columns",
                    exception="Missing required columns",
                )

            records = []
            for _, row in dftmp.iterrows():
                records.append(
                    {
                        "name_report": data.get("name"),
                        "name_customer": row["NOME"],
                        "cpf": row["CPF"],
                        "flat": row["FLAT"],
                        "number_proposal": row["NUMERO_PROPOSTA"],
                        "value_operation": row["VALOR_OPERACAO"],
                        "created_at": datetime.now(),
                        "user_id": self.user_id,
                        "is_payment": False,
                    }
                )

            if not records:
                logdb("warning", message="No records to insert.")
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="no_records_to_insert",
                )

            db.session.bulk_insert_mappings(self.report, records)
            db.session.commit()

            os.remove(filepath)
            return Response().response(
                status_code=200,
                error=False,
                message_id="report_add_successful",
            )

        except Exception as e:
            logdb("error", message=f"Error processing add report: {e}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_add_report",
                exception=str(e),
            )

    def list_report_imports(self, data: dict) -> None:
        try:
            current_page, rows_per_page = (
                int(data.get("current_page", 1)),
                int(data.get("rows_per_page", 10)),
            )

            current_page = max(current_page, 1)
            rows_per_page = max(rows_per_page, 1)

            pagination = Pagination().pagination(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=data.get("sort_by", ""),
                order_by=data.get("order_by", ""),
                filter_by=data.get("filter_by", ""),
                filter_value=data.get("filter_value", ""),
            )

            stmt = (
                select(
                    self.report.id,
                    self.report.name_report,
                    func.initcap(self.user.username).label("username"),
                    func.to_char(self.report.created_at, "YYYY-MM-DD").label(
                        "created_at"
                    ),
                )
                .distinct(self.report.name_report)
                .join(self.user, self.report.user_id == self.user.id)
                .where(
                    self.report.is_deleted == False,
                    self.user.is_deleted == False,
                )
                .order_by(
                    self.report.name_report, self.report.created_at.desc()
                )
            )

            # Filtro dinâmico
            if pagination["filter_value"]:
                filter_value = f"%{pagination['filter_value']}%"
                stmt = stmt.filter(self.report.name_report.ilike(filter_value))

            if pagination["order_by"]:
                sort_column = getattr(
                    self.report, pagination["order_by"], None
                )
                if sort_column is not None:
                    if pagination["sort_by"] == "asc":
                        stmt = stmt.order_by(sort_column.asc())
                    else:
                        stmt = stmt.order_by(sort_column.desc())
            else:
                stmt = stmt.order_by(self.report.id.desc())

            paginated_stmt = stmt.offset(pagination["offset"]).limit(
                pagination["limit"]
            )
            result = db.session.execute(paginated_stmt).fetchall()

            count_stmt = select(func.count()).select_from(
                select(self.report.id)
                .where(self.report.is_deleted == False)
                .where(
                    or_(
                        func.unaccent(self.report.name_report).ilike(
                            func.unaccent(filter_value)
                        )
                    )
                    if pagination["filter_value"]
                    else True
                )
                .subquery()
            )

            total = db.session.execute(count_stmt).scalar()
            if not result:
                return Response().response(
                    status_code=404, error=False, message_id="report_not_found"
                )

            metadata = Pagination().metadata(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=data.get("sort_by", ""),
                order_by=data.get("order_by", ""),
                filter_by=data.get("filter_by", ""),
                filter_value=data.get("filter_value", ""),
                total=total,
            )

            return Response().response(
                status_code=200,
                error=False,
                data=Metadata(result).model_to_list(),
                metadata=metadata,
            )

        except Exception as e:
            logdb("error", message=f"Error processing add report: {e}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_list_report",
                exception=str(e),
            )

    def delete_imports(self, name: str) -> None:
        try:
            stmt = (
                update(self.report)
                .where(self.report.name_report == name)
                .values(
                    is_deleted=True,
                    deleted_at=datetime.now(),
                    deleted_by=self.user_id,
                )
            )
            db.session.execute(stmt)
            db.session.commit()
            return Response().response(
                status_code=200,
                error=False,
                message_id="report_delete_successful",
            )
        except Exception as e:
            logdb("error", message=f"Error processing delete report: {e}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_delete_report",
                exception=str(e),
            )
