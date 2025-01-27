class FinancialAgreementsModels:

    def __init__(self, user_id: int) -> None:
        self.user_id = user_id

    def list_financial_agreements(self, pagination: dict):
        query_filter = ""
        if pagination["filter_by"]:
            query_filter = f"""AND (unaccent(b.name) ILIKE unaccent('%{pagination["filter_by"]}%'))"""

        query_order_by = ""
        if pagination["sort_by"] and pagination["order_by"]:
            query_order_by = f"""ORDER BY b.{pagination["order_by"]} {pagination["sort_by"]}"""

        query = f"""
            SELECT
                INITCAP(TRIM(b.name)) AS banker,
                INITCAP(TRIM(fa.name)) AS financial_agreements,
                b.id AS banker_id,
                fa.id AS id_financial_agreements
            FROM 
                public.financial_agreements AS fa
                INNER JOIN public.bankers b ON b.id=fa.banker_id
            WHERE b.is_deleted = false and fa.is_deleted = false {query_filter}
            {query_order_by}
            OFFSET {pagination["offset"]} LIMIT {pagination["limit"]};
        """
        return query

    def get_financial_agreements(self, id: int):
        query = f"""
            SELECT 
                INITCAP(TRIM(b.name)) as banker,
                INITCAP(TRIM(fa.name)) as financial_agreements,
                TO_CHAR(fa.create_at, 'YYYY-MM-DD') AS create_at,
                fa.is_deleted
            FROM 
                public.financial_agreements AS fa
                INNER JOIN public.bankers b ON b.id=fa.banker_id
            WHERE b.is_deleted = false AND fa.id = {id}
        """
        return query

    def add_financial_agreements(self, name: str, banker_id: int) -> None:
        query = f"""
            INSERT INTO public.financial_agreements (name, create_at, banker_id, is_deleted) 
            VALUES (
                '{name}', 
                NOW(),
                {banker_id},
                false
            ) 
            RETURNING name;
        """
        return query

    def update_financial_agreements(self, name: str, id: int) -> None:
        query = f"""
            UPDATE public.financial_agreements AS b
            set
                name='{name}'
            WHERE b.id = {id}
            RETURNING b.id;
        """
        return query

    def delete_financial_agreements(self, id: int):
        query = f"""
            UPDATE public.financial_agreements AS b
            set
                is_deleted=true,
                deleted_by= {self.user_id},
                deleted_at = NOW()
            WHERE b.id = {id}
            RETURNING b.name;
        """
        return query