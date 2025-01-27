class OperationaModel:
    
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        
    def list_proposal(self, pagination: dict):
        query_filter = ""
        if pagination["filter_by"]:
            query_filter = f"""AND (unaccent(p.cpf) ILIKE unaccent('%{pagination["filter_by"]}%')) OR (unaccent(cp.current_status) ILIKE unaccent('%{pagination["filter_by"]}%')) """
        
        query_order_by = ""
        if pagination["sort_by"] and pagination["order_by"]:
            query_order_by = f"""ORDER BY tf.{pagination["order_by"]} {pagination["sort_by"]}"""

        query = f"""
            WITH status_proposal AS (
                SELECT DISTINCT ON (ps.proposal_id)
                    ps.proposal_id,
                    u.username AS digitador_por,
                    mo.created_at AS digitado_as,
                    ps.action_at AS status_updated_at,
                    ps.action_by AS status_updated_by,
                    u.username AS status_updated_by_name,
                    CASE 
                        WHEN ps.contrato_pago THEN 'Contrato Pago'
                        WHEN ps.aguardando_digitacao THEN 'Aguardando Digitação'
                        WHEN ps.pendente_digitacao THEN 'Pendente de Digitação'
                        WHEN ps.contrato_em_digitacao THEN 'Contrato em Digitação'
                        WHEN ps.aguardando_pagamento THEN 'Aguardando Pagamento'
                        WHEN ps.aceite_feito_analise_banco THEN 'Aceite Feito - Análise Banco'
                        WHEN ps.contrato_pendente_banco THEN 'Contrato Pendente - Banco'
                    END AS current_status
                FROM 
                    public.proposal_status ps
                LEFT JOIN public.manage_operational mo ON mo.proposal_id = ps.proposal_id
                LEFT JOIN public.user u ON u.id = ps.action_by
                WHERE ps.is_deleted = FALSE
                ORDER BY ps.proposal_id, ps.created_at DESC
            )
            SELECT
                p.id,
                initcap(trim(u.username)) AS nome_digitador,
                initcap(trim(p.nome)) AS nome_cliente,
                p.cpf AS cpf_cliente,
                TO_CHAR(p.created_at, 'DD-MM-YYYY HH24:MI') AS data_criacao,
                cp.current_status,
                initcap(trim(lo.name)) AS tipo_operacao,
                TO_CHAR(cp.digitado_as, 'DD-MM-YYYY HH24:MI') AS digitado_as,
                initcap(trim(cp.digitador_por)) AS digitador_por
            FROM 
                proposal p 
            LEFT JOIN proposal_loan pl ON pl.proposal_id = p.id
            LEFT JOIN loan_operation lo ON lo.id = pl.loan_operation_id 
            LEFT JOIN status_proposal cp ON cp.proposal_id = p.id
            LEFT JOIN public.user u ON u.id = p.user_id
            WHERE p.is_deleted = FALSE AND pl.is_deleted = FALSE {query_filter}
            GROUP BY p.id, u.username, p.nome, p.cpf, p.created_at, cp.current_status, lo.name, cp.digitado_as, cp.digitador_por
            ORDER BY p.created_at DESC
            OFFSET {pagination["offset"]} LIMIT {pagination["limit"]};
        """
        return query

    def typing_proposal(self, proposal_id: int, data: dict):
        columns_register = {
            "aguardando_digitacao": data.get("aguardando_digitacao"),
            "pendente_digitacao": data.get("pendente_digitacao"),
            "contrato_em_digitacao": data.get("contrato_em_digitacao"),
            "aceite_feito_analise_banco": data.get("aceite_feito_analise_banco"),
            "contrato_pendente_banco": data.get("contrato_pendente_banco"),
            "aguardando_pagamento": data.get("aguardando_pagamento"),
            "contrato_pago": data.get("contrato_pago")
        }

        description = data.get("description", "")

        col_names = []
        col_values = []
        update_set = []

        for col, value in columns_register.items():
            if value is not None:
                col_names.append(col)
                if isinstance(value, str):
                    col_values.append(f"'{value}'")
                else:
                    col_values.append(value)
                update_set.append(f"{col} = {col_values[-1]}")

        if data.get("number_proposal") is None:
            query = f"""
                UPDATE proposal_status
                SET 
                    {', '.join(update_set)},
                    action_at = NOW(),
                    action_by = {self.user_id}
                WHERE proposal_id = {proposal_id};
                
                INSERT INTO history (proposal_id, user_id, description)
                VALUES ({proposal_id}, {self.user_id}, '{description}');                
            """
        else:
            number_proposal = data["number_proposal"]
            query = f"""
                UPDATE proposal_status
                SET {', '.join(update_set)}
                WHERE proposal_id = {proposal_id};
                                
                INSERT INTO manage_operational (number_proposal, proposal_id, created_at, user_id)
                VALUES ({number_proposal}, {proposal_id}, NOW(), {self.user_id})
                ON CONFLICT (proposal_id)
                DO UPDATE SET number_proposal = EXCLUDED.number_proposal, created_at = EXCLUDED.created_at, user_id = EXCLUDED.user_id;

                INSERT INTO history (proposal_id, user_id, description)
                VALUES ({proposal_id}, {self.user_id}, '{description}');
            """
        return query

    def count_proposal(self):
        query = f"""
            WITH count_proposal AS (
                SELECT
                    ps.proposal_id,
                    u.username AS digitador_por,
                    mo.created_at AS digitado_as,
                    CASE 
                        WHEN ps.contrato_pago THEN ps.action_at
                        WHEN ps.aguardando_digitacao THEN ps.action_at
                        WHEN ps.pendente_digitacao THEN ps.action_at
                        WHEN ps.contrato_em_digitacao THEN ps.action_at
                        WHEN ps.aceite_feito_analise_banco THEN ps.action_at
                        WHEN ps.contrato_pendente_banco THEN ps.action_at
                    END AS status_updated_at,
                    CASE 
                        WHEN ps.contrato_pago THEN ps.action_by
                        WHEN ps.aguardando_digitacao THEN ps.action_by
                        WHEN ps.pendente_digitacao THEN ps.action_by
                        WHEN ps.contrato_em_digitacao THEN ps.action_by
                        WHEN ps.aceite_feito_analise_banco THEN ps.action_by
                        WHEN ps.contrato_pendente_banco THEN ps.action_by
                    END AS status_updated_by,
                    CASE 
                        WHEN ps.contrato_pago THEN u.username
                        WHEN ps.aguardando_digitacao THEN u.username
                        WHEN ps.pendente_digitacao THEN u.username
                        WHEN ps.contrato_em_digitacao THEN u.username
                        WHEN ps.aceite_feito_analise_banco THEN u.username
                        WHEN ps.contrato_pendente_banco THEN u.username
                    END AS status_updated_by_name,
                    CASE 
                        WHEN ps.contrato_pago THEN 'Contrato Pago'
                        WHEN ps.aguardando_digitacao THEN 'Aguardando Digitação'
                        WHEN ps.pendente_digitacao THEN 'Pendente de Digitação'
                        WHEN ps.contrato_em_digitacao THEN 'Contrato em Digitação'
                        WHEN ps.aceite_feito_analise_banco THEN 'Aceite Feito - Análise Banco'
                        WHEN ps.contrato_pendente_banco THEN 'Contrato Pendente - Banco'
                    END AS current_status
                FROM public.proposal_status ps
                LEFT JOIN public.proposal p on ps.proposal_id = p.id
                LEFT JOIN public.manage_operational mo ON mo.proposal_id = ps.proposal_id
                LEFT JOIN public.user u ON u.id = ps.action_by
                WHERE p.is_deleted = FALSE
            )
            SELECT
                COUNT(*) AS total_pendente_digitacao
            FROM count_proposal
            WHERE current_status = 'Pendente de Digitação';
        """
        return query

    def history_proposal(self, pagination: dict, proposal_id: int):
        query_filter = ""
        if pagination["filter_by"]:
            query_filter = f"""AND (unaccent(p.cpf) ILIKE unaccent('%{pagination["filter_by"]}%'))"""
        
        query_order_by = ""
        if pagination["sort_by"] and pagination["order_by"]:
            query_order_by = f"""ORDER BY tf.{pagination["order_by"]} {pagination["sort_by"]}"""

        query = f"""
            SELECT 
                h.id AS id_historico,
                u.username AS criado_por,
                TO_CHAR(h.created_at , 'DD-MM-YYYY HH24:MI') AS criado_as,
                initcap(trim(h.description)) AS descricao 
            FROM public.history h
            INNER JOIN public.user AS u on h.user_id = u.id 
            WHERE h.proposal_id = {proposal_id}
            ORDER BY criado_as DESC
            OFFSET {pagination["offset"]} LIMIT {pagination["limit"]};
        """
        return query
      
    def details_proposal(self, id: int):
        query = f"""
            SELECT
                ps.proposal_id as proposal_id,
                ps.aguardando_digitacao,
                ps.pendente_digitacao,
                ps.contrato_em_digitacao,
                ps.aceite_feito_analise_banco,
                ps.contrato_pendente_banco,
                ps.aguardando_pagamento,
                ps.contrato_pago,
                mo.number_proposal 
            FROM proposal_status ps 
            LEFT JOIN manage_operational mo on mo.proposal_id = ps.proposal_id 
            WHERE ps.proposal_id = {id}
        """
        return query