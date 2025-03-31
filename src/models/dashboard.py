class DashBoardModels:
    
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id

    def sales_paid(self):
        query = f"""
            SELECT
                ROUND(SUM(COALESCE(pl.valor_operacao, 0))::numeric, 2)::money AS value_total_operations
            FROM
                proposal_loan pl
                INNER JOIN public.proposal_status ps ON ps.proposal_id = pl.proposal_id
            WHERE pl.is_deleted = false AND ps.contrato_pago = true
        """
        return query
    
    
    def status_proposals(self):
        query = f"""
            SELECT
                SUM(CASE WHEN aguardando_digitacao THEN 1 ELSE 0 END) AS aguardando_digitacao_count,
                SUM(CASE WHEN pendente_digitacao THEN 1 ELSE 0 END) AS pendente_digitacao_count,
                SUM(CASE WHEN contrato_em_digitacao THEN 1 ELSE 0 END) AS contrato_em_digitacao_count,
                SUM(CASE WHEN aceite_feito_analise_banco THEN 1 ELSE 0 END) AS aceite_feito_analise_banco_count,
                SUM(CASE WHEN contrato_pendente_banco THEN 1 ELSE 0 END) AS contrato_pendente_banco_count,
                SUM(CASE WHEN aguardando_pagamento THEN 1 ELSE 0 END) AS aguardando_pagamento_count,
                SUM(CASE WHEN contrato_pago THEN 1 ELSE 0 END) AS contrato_pago_count
            FROM 
                proposal_status ps
            WHERE ps.is_deleted = false;
        """
        return query

    def salles_sales_paid_ranking(self, pagination: dict):
        query_filter = ""
        if pagination["filter_by"]:
            query_filter = f"""AND (unaccent(u.username) ILIKE unaccent('%{pagination["filter_by"]}%'))"""

        query_order_by = ""
        if pagination["sort_by"] and pagination["order_by"]:
            query_order_by = f"""ORDER BY p.{pagination["order_by"]} {pagination["sort_by"]}"""
        
        query = f"""
            SELECT
                u.id AS seller_id,
                u.username AS seller,
                u.role AS role,
                ROUND(SUM(COALESCE(pl.valor_operacao, 0))::numeric, 2)::money AS value_total_operations
            FROM
                public.user u
            INNER JOIN public.proposal_loan pl ON pl.user_id = u.id
            INNER JOIN public.proposal_status ps ON ps.proposal_id = pl.proposal_id AND ps.user_id = u.id and ps.is_deleted = false
            WHERE
                u.is_deleted = false 
                AND ps.contrato_pago = true
                AND pl.is_deleted = false {query_filter}
            GROUP BY u.id, u.username, u.role
            ORDER BY value_total_operations DESC
            OFFSET {pagination["offset"]} LIMIT {pagination["limit"]};
        """
        return query
    