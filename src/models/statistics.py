
class StatisticsModel:
    
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        
    def list_hold_profit_sellers(self, pagination: dict):
        query_filter = ""
        if pagination["filter_by"]:
            query_filter = f""" (unaccent(ls.cpf_proposal) ILIKE unaccent('%{pagination["filter_by"]}%')) OR (unaccent(ls.name_seller) ILIKE unaccent('%{pagination["filter_by"]}%'))"""

        query_order_by = ""
        if pagination["sort_by"] and pagination["order_by"]:
            query_order_by = f"""ORDER BY tf.{pagination["order_by"]} {pagination["sort_by"]}"""
        
        query = f"""
            WITH list_statics AS (
                SELECT
                    u.id AS id_seller,
                    p.id AS id_proposal,
                    u.username AS name_seller,
                    p.nome AS nome_proposal,
                    p.cpf AS cpf_proposal,
                    ps.contrato_pago,
                    pl.valor_operacao,
                    ROUND(CAST(ROUND(CAST(pl.valor_operacao AS NUMERIC), 2) * tf.rate / 100 AS NUMERIC), 2) AS valor_comissionado
                FROM 
                    proposal p
                    INNER JOIN public.user u ON u.id = p.user_id
                    INNER JOIN public.proposal_status ps ON ps.proposal_id = p.id
                    INNER JOIN public.proposal_loan pl ON pl.proposal_id = p.id
                    INNER JOIN tables_finance tf ON tf.id = pl.tables_finance_id 
                WHERE u.id = {self.user_id}  AND u.is_deleted= FALSE AND ps.contrato_pago = TRUE AND p.is_deleted = FALSE AND tf.is_deleted = FALSE
                ORDER BY p.id, p.created_at ASC
            ), flags_sellers AS (
                SELECT 
                    ff.user_id,
                    f."name",
                    f.rate,
                    u.username AS sellers
                FROM 
                    flags_processing_payments ff
                    INNER JOIN public.flags f ON f.id = ff.flag_id 
                    INNER JOIN public.user u ON u.id = ff.user_id 
                WHERE u.id = {self.user_id} AND u.is_deleted = FALSE AND ff.user_id = {self.user_id}
            )
            SELECT
                initcap(trim(ls.name_seller)) AS name_seller,
                initcap(trim(ls.nome_proposal)) AS nome_proposal,
                ls.cpf_proposal,
                ls.contrato_pago,
                ls.valor_operacao,
                ROUND(CAST(ROUND(CAST(ls.valor_comissionado AS NUMERIC), 2) * fs.rate / 100 AS NUMERIC), 2)::float AS ganho_esperado
            FROM 
                flags_sellers fs
                INNER JOIN list_statics ls ON ls.id_seller = fs.user_id
            {"WHERE " + query_filter if query_filter else ""}
            GROUP BY ls.id_seller, ls.nome_proposal, ls.cpf_proposal, fs.name, ls.contrato_pago, ls.valor_operacao, ls.valor_comissionado, fs.rate, ls.name_seller
            OFFSET {pagination["offset"]} LIMIT {pagination["limit"]};
        """ 
        return query

    def list_ranking_sellers(self, pagination: dict):
        query_filter = ""
        if pagination["filter_by"]:
            query_filter = f"""AND (unaccent(u.username) ILIKE unaccent('%{pagination["filter_by"]}%'))"""

        query_order_by = ""
        if pagination["sort_by"] and pagination["order_by"]:
            query_order_by = f"""ORDER BY tf.{pagination["order_by"]} {pagination["sort_by"]}"""

        query = f"""
            SELECT
                u.id AS seller_id,
                u.username AS seller,
                u.role AS role,
                ROUND(SUM(COALESCE(pl.valor_operacao, 0))::numeric, 2)::money AS value_total_operations
            FROM
                public.user u
            INNER JOIN public.proposal_loan pl ON pl.user_id = u.id
            INNER JOIN public.proposal_status ps ON ps.proposal_id = pl.proposal_id AND ps.user_id = u.id
            WHERE
                u.is_deleted = false
                AND ps.is_deleted = false
                AND ps.contrato_pago = true
                AND pl.is_deleted = false {query_filter}
            GROUP BY u.id, u.username, u.role
            ORDER BY value_total_operations DESC
            OFFSET {pagination["offset"]} LIMIT {pagination["limit"]};
        """
        return query
    