class TablesFinanceModels:
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

    def add_tables(self, data: dict):  
        query = f"""
            INSERT INTO public.tables_finance (name, type_table, table_code, start_term, end_term, rate, is_status, financial_agreements_id, issue_date, create_at)
            VALUES (
                '{data.get("name")}',
                '{data.get("type_table")}',
                '{data.get("table_code")}',
                '{data.get("start_term")}',
                '{data.get("end_term")}',
                {data.get("rate")},
                false,
                {data.get("financial_agreements_id")},
                '{data.get("issue_date")}',
                NOW()
            );
        """
        return query

    def add_tables_finance(self, name: str, type_table: str, table_code: str, start_term: str, end_term: str, rate: float, financial_agreements_id: int, issue_date: str) -> None:
        query = f"""
            INSERT INTO public.tables_finance (name, type_table, table_code, start_term, end_term, rate, is_status, financial_agreements_id, issue_date, create_at)
            VALUES (
                '{name}',
                '{type_table}',
                '{table_code}',
                '{start_term}',
                '{end_term}',
                {rate},
                false,
                {financial_agreements_id},
                '{issue_date}',
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