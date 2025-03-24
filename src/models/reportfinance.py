## TODO - Quantitativo de propostas pagas e não pagas (Ex... Total ou por vendedor ou por sala)

"""
# TODO sobre o reportfinance
Ajuste no relatório de comissão paga

- Criar o fluxo de comissão paga [Deletar comissão paga] -> vai ficar no payment
- Ajustar o check do relatorios importados [Podendo removelos ou não] 
- Removendo a logica do flag do report finance -> foi para o arquivo flag.py
- Removendo a logica do processar pagamento do relatorio, e deixando consolidado e separado no arquivo payment
- Deixando somente a a logica do relatorio e checagem com as propostas pagas no arquivo `report`

"""




class ReportModels:

    def __init__(self, user_id: int, *args, **kwargs) -> None:
        self.user_id = user_id
            
    def add_report(self, batch_list):
        query = """
        INSERT INTO public.report_data (name, create_at, cpf, number_proposal, table_code, value_operation, is_validated, is_deleted, user_id) 
        VALUES 
        """
        
        values = []
        for record in batch_list:
            formatted_cpf = record[1].replace(".", "").replace("-", "")
            formatted_value = record[4] if isinstance(record[4], (int, float)) else f"'{record[4]}'"
            values.append(
                f"('{record[0]}', NOW(), '{formatted_cpf}', '{record[2]}', '{record[3]}', {formatted_value}, {record[5]}, FALSE, {self.user_id})"
            )

        query += ",\n".join(values) + ";"
        return query

    def list_check_report_proposal(self, report_name: str, pagination: dict):
        query_filter = ""
        if pagination["filter_by"]:
            query_filter = f"""AND (unaccent(rd.cpf) ILIKE unaccent('%{pagination["filter_by"]}%'))"""

        query = f"""
            SELECT
                distinct(p.id),
                u.username AS name_sellers,
                p.nome AS name_client,
                rd.cpf AS cpf_client, 
                pl.valor_operacao
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
                WHERE rd.is_deleted = false AND rd.name = '{report_name}' {query_filter}
            ORDER BY p.id
            OFFSET {pagination["offset"]} LIMIT {pagination["limit"]};
        """
        return query

    def list_import(self, pagination: dict):
        query_filter = ""
        if pagination["filter_by"]:
            query_filter = f"""AND (unaccent(rd.name) ILIKE unaccent('%{pagination["filter_by"]}%'))"""

        query = f"""
            SELECT 
                distinct(name),
                initcap(trim(u.username)) AS username,
                TO_CHAR(rd.create_at, 'YYYY-MM-DD HH:MM:SS') AS created_at
            FROM 
                report_data rd 
            INNER JOIN public.user u ON u.id = rd.user_id
            WHERE rd.is_deleted = false {query_filter}
            ORDER BY created_at DESC;
        """
        return query
    
    def delete_import(self, name: str):
        query = f"""
            DELETE FROM report_data WHERE name = '{name}';
        """
        return query

    def export_report(self):
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