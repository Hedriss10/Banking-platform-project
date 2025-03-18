from typing import Optional, Dict
from src.utils.log import logs_and_save_db

class TablesFinanceModels:
    name: Optional[str] = None
    type_table: Optional[str] = None
    table_code: Optional[str] = None
    start_term: Optional[str] = None
    end_term: Optional[str] = None
    rate: float = 0.0
    financial_agreements_id: int = 0
    issue_date: Optional[str] = None
    start_rate: str
    end_rate: str
    
    # check arguments
    def validate(self) -> bool:
        missing_fields = [
            field for field, value in self.__dict__.items() if value is None
        ]
        if missing_fields:
            logs_and_save_db("warning", message=f"Not arguments invalid {missing_fields}")
            return False
        return True

    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id

    def rank_comission(self, pagination: dict) -> None:
        query_filter = ""
        if pagination["filter_by"]:
            query_filter = f"""AND (unaccent(tf.table_code) ILIKE unaccent('%{pagination["filter_by"]}%')) OR (unaccent(tf.name) ILIKE unaccent('%{pagination["filter_by"]}%')) """

        query_order_by = ""
        if pagination["sort_by"] and pagination["order_by"]:
            query_order_by = f"""ORDER BY tf.{pagination["order_by"]} {pagination["sort_by"]}"""

        query = f"""
            SELECT
                tf.id,
                initcap(trim(tf.name)) AS table,
                initcap(trim(b.name)) AS name_banker,
                tf.table_code,
                tf.rate,
                tf.start_term,
                tf.end_term
            FROM 
                tables_finance tf
                INNER JOIN public.financial_agreements fa ON fa.id = tf.financial_agreements_id
                INNER JOIN public.bankers b ON b.id = fa.banker_id 
            WHERE tf.is_deleted = false {query_filter} AND fa.is_deleted = false AND b.is_deleted = false
            GROUP BY tf.id, b.id, fa.id
            ORDER BY tf.id asc
            OFFSET {pagination["offset"]} LIMIT {pagination["limit"]};
        """
        return query

    def add_tables(self, data: Dict[str, str]) -> str:
        self.name = data.get("name")
        self.type_table = data.get("type_table")
        self.table_code = data.get("table_code")
        self.start_term = data.get("start_term")
        self.end_term = data.get("end_term")
        self.rate = float(data.get("rate", 0.0))
        self.financial_agreements_id = int(data.get("financial_agreements_id", 0))
        self.issue_date = data.get("issue_date")
        self.start_rate = data.get("start_rate", "")
        self.end_rate = data.get("end_rate", "")
        
        if not self.validate():
            raise ValueError("Invalid arguments")
        
        query = f"""
            INSERT INTO public.tables_finance (name, type_table, table_code, start_term, end_term, rate, is_status, financial_agreements_id, issue_date, start_rate, end_rate, created_at)
            VALUES (
                '{data.get("name")}',
                '{data.get("type_table")}',
                '{data.get("table_code")}',
                '{data.get("start_term")}',
                '{data.get("end_term")}',
                {data.get("rate")},
                FALSE,
                {data.get("financial_agreements_id")},
                '{data.get("issue_date")}',
                '{data.get("start_rate", "")}',
                '{data.get("end_rate", "")}',
                NOW()
            );
        """
        return query

    def add_tables_finance(self, data: dict, financial_agreements_id: int, issue_date: str) -> str:
        query = f"""
            INSERT INTO public.tables_finance (name, type_table, table_code, start_term, end_term, rate, is_status, financial_agreements_id, issue_date, start_rate, end_rate, created_at)
            VALUES (
                '{data.get("name")}',
                '{data.get("type_table")}',
                '{data.get("table_code")}',
                '{data.get("start_term")}',
                '{data.get("end_term")}',
                {data.get("rate")},
                FALSE,
                {financial_agreements_id},
                '{issue_date}',
                '{data.get("start_rate", "")}',
                '{data.get("end_rate", "")}',
                NOW()
            );
        """
        return query

    def list_board_tables(self, pagination: dict, financial_agreements: int) -> None:
        query_filter = ""
        if pagination["filter_by"]:
            query_filter = f"""AND (unaccent(tf.name) ILIKE unaccent('%{pagination["filter_by"]}%')) OR (unaccent(tf.table_code) ILIKE unaccent('%{pagination["filter_by"]}%'))"""

        query_order_by = ""
        if pagination["sort_by"] and pagination["order_by"]:
            query_order_by = f"""ORDER BY b.{pagination["order_by"]} {pagination["sort_by"]}"""

        query = f"""
            SELECT 
                id,
                name,
                type_table,
                table_code,
                start_term,
                end_term,
                rate
            FROM 
                tables_finance as tf
            WHERE tf.financial_agreements_id = {financial_agreements} AND tf.is_deleted = false {query_filter}
            GROUP BY tf.id
            {query_order_by}
            OFFSET {pagination["offset"]} LIMIT {pagination["limit"]};
        """
        return query

    def delete_tables_ids(self, financial_agreements_id: int, ids: dict) -> None:
        ids_str = ', '.join(map(str, ids))
        query = f"""
            UPDATE public.tables_finance AS tf
                SET is_deleted = TRUE
            WHERE tf.financial_agreements_id = {financial_agreements_id} AND tf.id IN ({ids_str});
        """
        return query
