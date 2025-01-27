class BankerFinanceModels:

    def __init__(self, user_id: int) -> None:
        self.user_id = user_id

    def list_bankers(self, pagination: dict):
        query_filter = ""
        if pagination["filter_by"]:
            query_filter = f"""AND (unaccent(b.name) ILIKE unaccent('%{pagination["filter_by"]}%'))"""

        query_order_by = ""
        if pagination["sort_by"] and pagination["order_by"]:
            query_order_by = f"""ORDER BY b.{pagination["order_by"]} {pagination["sort_by"]}"""

        query = f"""
            SELECT 
                b.id,
                INITCAP(TRIM(b.name)) as name,
                TO_CHAR(b.create_at, 'YYYY-MM-DD') AS create_at
            FROM 
                bankers b
            WHERE b.is_deleted = false {query_filter}
            {query_order_by}
            GROUP BY b.id
            OFFSET {pagination["offset"]} LIMIT {pagination["limit"]};
        """
        return query

    def get_banker(self, id: int):
        query = f"""
            SELECT
                fa.id,
                INITCAP(TRIM(fa.name)) AS name_financial_agreements
            FROM 
                financial_agreements fa
            INNER JOIN bankers b on fa.banker_id = b.id
            WHERE fa.is_deleted = false AND b.id = {id} AND fa.is_deleted = false AND fa.is_deleted = false
            ORDER BY fa.id
        """
        return query

    def add_bankers(self, name: str) -> None:
        query = f"""
            INSERT INTO public.bankers (name, create_at, is_deleted) 
            VALUES (
                '{name}', 
                NOW(), 
                false
            )
            RETURNING id;
        """
        return query

    def update_bankers(self, name: str, id: int) -> None:
        query = f"""
            UPDATE public.bankers AS b
            set
                name='{name}'
            WHERE b.id = {id}
            RETURNING b.name
        """
        return query

    def delete_bankers(self, id: int):
        query = f"""
            UPDATE public.bankers AS b
            set
                is_deleted=true,
                deleted_by={self.user_id},
                deleted_at = NOW()
            WHERE b.id = {id}
            RETURNING b.name
        """
        return query