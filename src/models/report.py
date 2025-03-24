"""

- checando os relatorios com o check report, onde podemos encontrar o \\
    o CPF do cliente e o CPF do vendedor e o valor da comissão, \\
        com o valor da operação e codigo de tabela
        
- removendo o namesapce de `reportfinance` para `report.py`
- Ajustando o swagger 

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
