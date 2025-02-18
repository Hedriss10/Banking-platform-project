## TODO refatorar a listagem de convenios com os bancos - > removida
## TODO mandar um dict sobre os convenios e bancos


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

    def get_banker(self, banker_id: int):
        query = f"""
            SELECT
                b.id AS bank_id,
                fa.id AS financial_agreements_id,
                initcap(trim(b.name)) AS name_bank,
                json_agg(
                    json_build_object(
                        'id_financialagreements', fa.id,
                        'financialagreements_name', initcap(trim(fa.name))
                    )
                ) AS financial_agreements
            FROM 
                public.bankers b
                LEFT JOIN public.financial_agreements fa ON b.id = fa.banker_id AND fa.is_deleted = false
            WHERE b.is_deleted = false AND b.id = {banker_id}
            GROUP BY b.id, b.name, fa.id;
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

    def update_bankers(self, name: str, id: int) -> None:
        query = f"""
            UPDATE public.bankers AS b
            SET
                name='{name}'
            WHERE b.id = {id}
            RETURNING b.name
        """
        return query

    def delete_bankers(self, banker_id: int):
        query = f"""
            WITH updated AS (
                UPDATE public.bankers AS b
                SET
                    is_deleted = true,
                    deleted_by = {self.user_id},
                    deleted_at = NOW()
                WHERE b.id = {banker_id}
                RETURNING b.name
            )
            SELECT 
                CASE 
                    WHEN EXISTS (SELECT 1 FROM updated) THEN true
                    ELSE false
                END AS banker_exists;
        """
        return query
    
    def update_financial_agreements(self, name: str, id: int) -> None:
        query = f"""
            UPDATE public.financial_agreements AS b
            SET
                name='{name}'
            WHERE b.id = {id}
            RETURNING b.id;
        """
        return query
    
    def delete_financial_agreements(self, id: int):
        query = f"""
            UPDATE public.financial_agreements AS b
            SET
                is_deleted=true,
                deleted_by= {self.user_id},
                deleted_at = NOW()
            WHERE b.id = {id}
            RETURNING b.name;
        """
        return query