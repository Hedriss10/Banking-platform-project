from typing import Dict, List, Optional


class PayamentsModels:
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id

    def report_validated(self, number_proposal: list):
        conditions = " OR ".join(f""" (number_proposal = '{item['number_proposal']}') """ for item in number_proposal)
        query = f"""
            UPDATE report_data 
            SET is_validated = true
            WHERE {conditions};
        """
        return query

    def list_sellers(self, name_report: str, has_report: str, pagination: dict):
        query_filter = ""
        if pagination.get("filter_by"):
            query_filter = f"""WHERE (unaccent(username) ILIKE unaccent('%{pagination["filter_by"]}%') OR unaccent(cpf) ILIKE unaccent('%{pagination["filter_by"]}%'))"""

        query_order_by = ""
        if pagination.get("sort_by") and pagination.get("order_by"):
            query_order_by = f"""ORDER BY {pagination["order_by"]} {pagination["sort_by"]}"""

        list_has_report = []
        where_has_report = []
        _name_report = ""
        if has_report.lower() == "true":
            list_has_report.append("""
            INNER JOIN associated_proposals ap ON ap.proposal_id = p.id
            INNER JOIN public.proposal_loan pl ON pl.proposal_id = p.id
            INNER JOIN public.report_data rd ON rd.id = ap.report_id
            INNER JOIN public.proposal_status ps ON ps.proposal_id = p.id
            INNER JOIN public.user u ON u.id = p.user_id
            """)
            where_has_report.append(f"""
            AND ap.proposal_id IS NOT NULL
            """)
            _name_report = f"""AND rd.name = '{name_report}' """
        else:
            list_has_report.append("""
            LEFT JOIN associated_proposals ap ON ap.proposal_id = p.id
            LEFT JOIN public.proposal_loan pl ON pl.proposal_id = p.id
            LEFT JOIN public.report_data rd ON rd.id = ap.report_id
            LEFT JOIN public.proposal_status ps ON ps.proposal_id = p.id
            LEFT JOIN public.user u ON u.id = p.user_id
            """)
            where_has_report.append("""
            AND ap.proposal_id IS NULL
            """)

        query = f"""
            WITH associated_proposals AS (
                SELECT
                    DISTINCT
                    p.id AS proposal_id,
                    u.username AS name_sellers,
                    rd.id AS report_id
                FROM 
                    proposal p
                    INNER JOIN public.user u ON u.id = p.user_id
                    INNER JOIN public.proposal_loan pl ON pl.proposal_id = p.id
                    INNER JOIN public.proposal_status ps ON ps.proposal_id = p.id
                    INNER JOIN public.manage_operational mo ON mo.proposal_id = p.id
                    INNER JOIN public.report_data rd ON rd.cpf = p.cpf
                    INNER JOIN public.tables_finance tf ON tf.table_code = rd.table_code 
                        AND rd.number_proposal::bigint = mo.number_proposal 
                        AND pl.valor_operacao = CAST(rd.value_operation AS double precision)
                WHERE
                    rd.is_deleted = false
                    AND p.is_deleted = false
                    {_name_report}
            ),
            decision_maker AS (
                SELECT
                    DISTINCT
                    u.id,
                    u.username,
                    u.cpf,
                    u.role
                FROM 
                    proposal p
                {list_has_report[0] if list_has_report[0] else list_has_report}
                WHERE 
                    p.is_deleted = false
                    AND u.is_deleted = false
                    AND u.is_block = false
                    AND u.is_acctive = true
                    AND ps.contrato_pago = true
                    AND NOT EXISTS (
                        SELECT 1
                        FROM flags_processing_payments fpp
                        WHERE fpp.proposal_id = p.id AND fpp.is_payment = true AND fpp.is_deleted = false
                    )
                    {where_has_report[0] if where_has_report else where_has_report}
            )
            SELECT 
                DISTINCT
                *
            FROM decision_maker AS dm {query_filter}
            OFFSET {pagination.get("offset", 0)} LIMIT {pagination.get("limit", 10)};
        """
        return query
    
    def list_decision_maker(self, ids: int):
        ids_str = ', '.join(map(str, ids))
        query = f"""
            SELECT 
                p.id AS proposal_id,
                u.id AS sellers_id
            FROM 
                proposal p
                INNER JOIN public.user u ON u.id = p.user_id
                INNER JOIN public.proposal_status ps ON ps.proposal_id = p.id
            WHERE p.is_deleted = false
                AND u.is_deleted = false AND u.is_block = false
                AND ps.contrato_pago = true  
                AND NOT EXISTS (
                    SELECT 1
                    FROM flags_processing_payments fpp
                    WHERE fpp.proposal_id = p.id AND fpp.is_payment = true AND fpp.is_deleted = false
                ) AND u.id IN({ids_str});
        """
        return query

    def check_proposal(self, ids: int):
        ids_str = ', '.join(map(str, ids))
        query = f"""
            SELECT DISTINCT
                mo.proposal_id,
                mo.number_proposal,
                u.id AS sellers_id
            FROM 
                proposal p
                INNER JOIN public.user u on u.id = p.user_id
                INNER JOIN public.proposal_loan pl ON pl.proposal_id = p.id
                INNER JOIN public.proposal_status ps ON ps.proposal_id = p.id
                INNER JOIN public.manage_operational mo ON mo.proposal_id = p.id
                INNER JOIN public.report_data rd ON rd.cpf = p.cpf
                INNER JOIN public.tables_finance tf ON tf.table_code = rd.table_code AND rd.number_proposal::bigint = mo.number_proposal AND pl.valor_operacao = CAST(rd.value_operation AS double precision)
            WHERE 
                rd.is_deleted = false 
                AND p.is_deleted = false
                AND u.id IN ({ids_str})
            ORDER BY mo.proposal_id;
        """
        return query
        
    def processing_payment(self, proposals: list, data: dict, user_ids: list):
        flag_id = data.get("flag_id")
        
        valid_sellers = {user['sellers_id'] for user in user_ids}

        values = ", ".join(
            f"({proposal['sellers_id']}, {flag_id}, {proposal['proposal_id']}, now(), {self.user_id}, TRUE)"
            for proposal in proposals
            if proposal['sellers_id'] in valid_sellers
        )
                
        query = f"""
            INSERT INTO public.flags_processing_payments (user_id, flag_id, proposal_id, created_at, created_by, is_payment)
            VALUES {values};
        """
        return query
     
    def export_payaments(self):
        query = f"""
            WITH processing_payments AS (
                SELECT 
                    p.cpf,
                    u.username,
                    mo.number_proposal AS number_proposal,
                    pl.valor_operacao AS value_operation,
                    tf.rate AS taxe_comission,
                    ROUND(CAST(ROUND(CAST(pl.valor_operacao AS NUMERIC), 2) * tf.rate / 100 AS NUMERIC), 2) AS value_base,
                    fl.rate AS taxe_repasse,
                    ROUND(CAST((fl.rate * ROUND(CAST(ROUND(CAST(pl.valor_operacao AS NUMERIC), 2) * tf.rate / 100 AS NUMERIC), 2) / 100) AS NUMERIC), 2) AS comission,
                    tf.table_code AS table_code,
                    TO_CHAR(w.created_at, 'DD-MM-YYYY HH24:MI:SS') AS created_at,
                    TO_CHAR(w.updated_at, 'DD-MM-YYYY HH24:MI:SS') AS updated_at
                FROM 
                    proposal p
                    INNER JOIN public.manage_operational mo ON mo.proposal_id = p.id
                    INNER JOIN public.user u ON u.id = p.user_id
                    INNER JOIN public.proposal_loan pl ON pl.proposal_id = p.id 
                    INNER JOIN public.tables_finance tf ON tf.id = pl.tables_finance_id
                    INNER JOIN public.flags_processing_payments w ON w.proposal_id = p.id
                    INNER JOIN public.flags fl on fl.id = w.flag_id
                    INNER JOIN public.proposal_status ps ON ps.proposal_id = p.id
                WHERE ps.contrato_pago = true
            )
            SELECT * FROM processing_payments as ps
        """
        return query
    
    def list_processing_payments(self, pagination: dict):
        query_filter = ""
        if pagination["filter_by"]:
            query_filter = f"""AND (unaccent(p.cpf) ILIKE unaccent('%{pagination["filter_by"]}%')) OR (unaccent(u.username) ILIKE unaccent('%{pagination["filter_by"]}%')) """

        query_order_by = ""
        if pagination["sort_by"] and pagination["order_by"]:
            query_order_by = f"""ORDER BY p.{pagination["order_by"]} {pagination["sort_by"]}"""

        query = f"""
            WITH processing_payments AS (
                SELECT 
                    w.id,
                    p.cpf,
                    u.username,
                    mo.number_proposal AS number_proposal,
                    pl.valor_operacao AS value_operation,
                    tf.rate AS taxe_comission,
                    ROUND(CAST(ROUND(CAST(pl.valor_operacao AS NUMERIC), 2) * tf.rate / 100 AS NUMERIC), 2) AS value_base,
                    fl.rate AS taxe_repasse,
                    ROUND(CAST((fl.rate * ROUND(CAST(ROUND(CAST(pl.valor_operacao AS NUMERIC), 2) * tf.rate / 100 AS NUMERIC), 2) / 100) AS NUMERIC), 2) AS comission,
                    tf.table_code AS table_code,
                    TO_CHAR(w.created_at, 'DD-MM-YYYY HH24:MI:SS') AS created_at,
                    TO_CHAR(w.updated_at, 'DD-MM-YYYY HH24:MI:SS') AS updated_at
                FROM 
                    proposal p
                    INNER JOIN public.manage_operational mo ON mo.proposal_id = p.id
                    INNER JOIN public.user u ON u.id = p.user_id
                    INNER JOIN public.proposal_loan pl ON pl.proposal_id = p.id 
                    INNER JOIN public.tables_finance tf ON tf.id = pl.tables_finance_id
                    INNER JOIN public.flags_processing_payments w ON w.proposal_id = p.id
                    INNER JOIN public.flags fl on fl.id = w.flag_id
                    INNER JOIN public.proposal_status ps ON ps.proposal_id = p.id
                WHERE ps.contrato_pago = true AND p.is_deleted= false AND u.is_deleted = false AND u.is_block = false AND w.is_deleted = false {query_filter}
            )
            SELECT * FROM processing_payments as ps
            OFFSET {pagination["offset"]} LIMIT {pagination["limit"]};
        """
        return query

    def delete_processing_payment(self, ids: list):
        ids_str = ', '.join(map(str, ids))
        query = f"""
            UPDATE flags_processing_payments 
            SET
                is_deleted = true,
                updated_at = NOW(),
                updated_by = {self.user_id}
            WHERE id IN ({ids_str});
        """
        return query