class SellerModels:
    def __init__(self, user_id: int, *args, **kwargs) -> None:
        self.user_id = user_id

    def list_proposal(self, pagination: dict) -> None:
        query_filter = ""
        if pagination["filter_by"]:
            query_filter = f"""AND (unaccent(p.cpf) ILIKE unaccent('%{pagination["filter_by"]}%')) OR (unaccent(u.username) ILIKE unaccent('%{pagination["filter_by"]}%'))"""

        query_order_by = ""
        if pagination["sort_by"] and pagination["order_by"]:
            query_order_by = f"""ORDER BY tf.{pagination["order_by"]} {pagination["sort_by"]}"""

        query = f"""
            WITH contract_paid_cte AS (
                SELECT
                    ps.proposal_id,
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
                    LEFT JOIN public.user u ON u.id = ps.action_by
            )
            SELECT
                p.id,
                initcap(trim(u.username)) AS username,
                initcap(trim(p.nome)) AS client_proposal,
                TO_CHAR(p.created_at, 'YYYY-MM-DD HH24:MI') AS created_at,
                p.cpf,
                initcap(trim(lo.name)) AS type_operation,
                TO_CHAR(p.updated_at, 'YYYY-MM-DD HH24:MI') AS updated_at,
                initcap(trim(cp.status_updated_by_name)) AS status_updated_by_name,
                cp.current_status
            FROM 
                public.proposal p
                LEFT JOIN public.user u ON u.id = p.user_id
                LEFT JOIN public.proposal_loan pl ON pl.proposal_id = p.id
                LEFT JOIN public.loan_operation lo ON lo.id = pl.loan_operation_id
                LEFT JOIN contract_paid_cte cp ON cp.proposal_id = p.id
            WHERE p.is_deleted = false AND p.user_id = {self.user_id} AND u.is_deleted=FALSE {query_filter}
            GROUP BY p.id, u.username, lo.name, cp.status_updated_by_name, cp.current_status
            ORDER BY p.created_at DESC
            OFFSET {pagination["offset"]} LIMIT {pagination["limit"]};
        """
        return query

    def add_proposal(self, data: dict) -> str:
        columns_register = [
            "nome",
            "data_nascimento",
            "genero",
            "email",
            "cpf",
            "naturalidade",
            "cidade_naturalidade",
            "uf_naturalidade",
            "cep",
            "data_emissao",
            "uf_cidade",
            "rg_documento",
            "orgao_emissor",
            "uf_emissor",
            "nome_mae",
            "nome_pai",
            "bairro",
            "endereco",
            "numero_endereco",
            "complemento_endereco",
            "cidade",
            "valor_salario",
            "salario_liquido",
            "telefone",
            "telefone_residencial",
            "telefone_comercial",
            "observe",
        ]

        col_names = []
        col_values = []

        for col in columns_register:
            if col in data and data[col] is not None:
                col_names.append(col)
                col_values.append(f"'{data[col]}'" if isinstance(data[col], str) else data[col])
            else:
                col_names.append(col)
                col_values.append("NULL")

        col_names.append("user_id")
        col_values.append(self.user_id)

        # Dynamic Query
        query = f"""
            INSERT INTO public.proposal ({', '.join(col_names)})
            VALUES ({', '.join(map(str, col_values))})
            RETURNING id;
        """
        return query

    def status_proposal(self, proposal_id: int):
        query = f"""
            INSERT INTO proposal_status (proposal_id, user_id, aguardando_digitacao, pendente_digitacao, contrato_em_digitacao, aceite_feito_analise_banco, contrato_pendente_banco, aguardando_pagamento, created_at) VALUES (
                {proposal_id}, {self.user_id}, false, true, false, false, false, false, now() 
            );
        """
        return query

    def proposal_benefit(self, benefit_id: int, proposal_id: int) -> str:
        if benefit_id is None:
            benefit_id = """ NULL """

        query = f"""
            INSERT INTO public.proposal_benefit (benefit_id, proposal_id) VALUES ({benefit_id}, {proposal_id});
        """
        return query

    def proposal_wallet(self, data: dict, proposal_id: int):
        columns_register = [
            ("agencia_banco", data.get("agencia_banco")),
            ("pix_chave", data.get("pix_chave")),
            ("numero_conta", data.get("numero_conta")),
            ("tipo_pagamento", data.get("tipo_pagamento")),
            ("agency_dvop", data.get("agency_dvop")),
            ("agencia_dv", data.get("agencia_dv")),
            ("agencia_op", data.get("agencia_op")),
            ("tipo_conta", data.get("tipo_conta")),
            ("user_id", self.user_id),
            ("proposal_id", proposal_id),
        ]

        col_names = [col for col, _ in columns_register]
        col_values = [f"'{value}'" if isinstance(value, str) else value if value is not None else "NULL" for _, value in columns_register]

        query = f"""
            INSERT INTO public.proposal_wallet ({', '.join(col_names)})
            VALUES ({', '.join(map(str, col_values))});
        """
        return query

    def proposal_loan(self, data: dict, proposal_id: int):
        data = data.to_dict(flat=True)

        int_fields = ['tables_finance_id', 'financial_agreements_id', 'loan_operation_id']

        for field in int_fields:
            if data.get(field) is not None:
                try:
                    data[field] = int(data[field])
                except ValueError:
                    raise ValueError(f"Campo {field} precisa ser um número inteiro válido.")

        columns_register = {
            "senha_servidor": data.get("senha_servidor"),
            "matricula": data.get("matricula"),
            "data_dispacho": data.get("data_dispacho"),
            "margem": data.get("margem"),
            "prazo_inicio": data.get("prazo_inicio"),
            "prazo_fim": data.get("prazo_fim"),
            "valor_operacao": data.get("valor_operacao"),
            "proposal_id": proposal_id,
            "tables_finance_id": data.get("tables_finance_id"),
            "financial_agreements_id": data.get("financial_agreements_id"),
            "loan_operation_id": data.get("loan_operation_id"),
            "user_id": self.user_id,
        }

        col_names = []
        col_values = []

        for col, value in columns_register.items():
            col_names.append(col)
            if value is None:
                col_values.append("NULL")
            elif isinstance(value, str):
                col_values.append(f"'{value}'")
            else:
                col_values.append(value)

        query = f"""
            INSERT INTO proposal_loan ({', '.join(col_names)})
            VALUES ({', '.join(map(str, col_values))});
        """
        return query

    def delete_proposal(self, proposal_id: int):
        query = f"""
            BEGIN;
                UPDATE public.proposal p
                SET 
                    is_deleted = true,
                    deleted_at = now()
                WHERE p.id = {proposal_id};

                UPDATE public.proposal_benefit as pb
                SET  
                    is_deleted = true,
                    deleted_at = now()
                WHERE pb.proposal_id = {proposal_id};
                
                UPDATE public.proposal_loan as pl
                SET 
                    is_deleted = true,
                    deleted_by = {self.user_id},
                    deleted_at = now()
                WHERE pl.proposal_id = {proposal_id};

                UPDATE public.proposal_status as ps
                SET 
                    deleted_by = {self.user_id},
                    deleted_at = now(),
                    is_deleted = true
                WHERE ps.proposal_id = {proposal_id};

                UPDATE public.proposal_wallet pw
                SET 
                    is_deleted = true,
                    deleted_at = now()
                WHERE pw.proposal_id = {proposal_id};
            COMMIT;
        """
        return query

    def update_proposal(self, proposal_id: int, data: dict):
        tables_and_fields = {
            "proposal": [
                "nome",
                "data_nascimento",
                "genero",
                "email",
                "cpf",
                "naturalidade",
                "cidade_naturalidade",
                "uf_naturalidade",
                "cep",
                "data_emissao",
                "uf_cidade",
                "rg_documento",
                "orgao_emissor",
                "uf_emissor",
                "nome_mae",
                "nome_pai",
                "bairro",
                "endereco",
                "numero_endereco",
                "complemento_endereco",
                "cidade",
                "valor_salario",
                "salario_liquido",
                "telefone",
                "telefone_residencial",
                "telefone_comercial",
                "observe",
            ],
            "proposal_wallet": ["agencia_banco", "pix_chave", "agencia", "agencia_dv", "agencia_op", "tipo_conta", "tipo_pagamento"],
            "proposal_loan": ["senha_servidor", "matricula", "data_dispacho", "margem", "prazo_inicio", "prazo_fim", "valor_operacao", "tables_finance_id", "financial_agreements_id", "loan_operation_id"],
            "proposal_benefit": [
                "benefit_id",
            ]
        }
        
        set_clauses = []
        params = []

        for table, fields in tables_and_fields.items():
            set_clauses_for_table = []
            
            for key, value in data.items():
                if key in fields and value not in (None, '', ' '):
                    if isinstance(value, str):
                        set_clauses_for_table.append(f"""{key} = '{value.strip()}' """)
                    else:
                        set_clauses_for_table.append(f"""{key} = {value}""")

            if set_clauses_for_table:
                set_clauses_for_table.append("updated_at = now()")
                set_clauses_for_table.append(f"updated_by = {self.user_id}")
                if table == "proposal":
                    set_clauses.append(f"UPDATE public.{table} p SET {', '.join(set_clauses_for_table)} WHERE p.id = {proposal_id}")
                elif table:
                    set_clauses.append(f"UPDATE public.{table} t SET {', '.join(set_clauses_for_table)} WHERE t.proposal_id = {proposal_id}")
                elif table:
                    set_clauses.append(f"UPDATE public.{table} b SET {', '.join(set_clauses_for_table)} WHERE b.proposal_id = {proposal_id}")
                elif table:
                    set_clauses.append(f"UPDATE public.{table} bp {', '.join(set_clauses_for_table)} WHERE bp.proposal_id = {proposal_id} ")

        if set_clauses:
            query = ";\n".join(set_clauses) + ";\n"
            return query, params
        else:
            return "No valid fields to update", []

    def get_proposal(self, id: int):
        query = f"""
            with get_proposal AS (
                SELECT
                    u.id AS id_seller,
                    initcap(trim(u.username)) AS name_seller,
                    p.id,
                    initcap(trim(p.nome)) AS nome,
                    p.genero,
                    p.email,
                    p.cpf,
                    p.rg_documento,
                    TO_CHAR(p.data_emissao, 'DD-MM-YYYY HH24:MI') AS data_emissao,
                    p.naturalidade,
                    p.cidade_naturalidade,
                    p.uf_naturalidade,
                    p.orgao_emissor,
                    p.uf_emissor,
                    initcap(trim(p.nome_mae)) AS nome_mae,
                    initcap(trim(p.nome_pai)) AS nome_pai,
                    initcap(trim(p.bairro)) AS bairro,
                    initcap(trim(p.endereco)) AS endereco,
                    p.numero_endereco,
                    p.complemento_endereco,
                    initcap(trim(p.cidade)) AS cidade,
                    p.valor_salario,
                    p.salario_liquido,
                    p.telefone,
                    p.uf_cidade,
                    p.cep,
                    TO_CHAR(p.data_nascimento, 'DD-MM-YYYY HH24:MI') AS data_nascimento,
                    p.telefone_residencial,
                    p.telefone_comercial,
                    TO_CHAR(p.created_at, 'DD-MM-YYYY HH24:MI') AS created_at,
                    lo.senha_servidor,
                    lo.matricula,
                    TO_CHAR(lo.data_dispacho, 'DD-MM-YYYY HH24:MI') AS data_dispacho,
                    lo.margem,
                    lo.prazo_inicio,
                    lo.prazo_fim,
                    lo.valor_operacao,
                    initcap(trim(b.name)) AS banker_name,
                    initcap(trim(fa.name)) AS name_financial_agreements,
                    lop.id as type_table,
                    initcap(trim(lop.name)) AS tipo_operacao,
                    tf.id as id_tabela,
                    tf.name as nome_tabela,
                    pw.agencia_banco,
                    pw.pix_chave,
                    pw.numero_conta,
                    pw.agencia_dv,
                    pw.agencia_op,
                    pw.agency_dvop,
                    initcap(trim(pw.tipo_conta)) AS tipo_conta,
                    pw.tipo_pagamento,
                    bt.id as id_beneficio,
                    initcap(trim(bt.name)) AS tipo_beneficio,
                    initcap(trim(p.observe)) AS observe
                FROM 
                    proposal AS p
                    INNER JOIN public.user u ON u.id = p.user_id
                    LEFT JOIN public.proposal_loan lo ON lo.proposal_id = p.id
                    LEFT JOIN public.tables_finance tf ON tf.id = lo.tables_finance_id
                    LEFT JOIN public.loan_operation lop on lop.id = lo.loan_operation_id
                    LEFT JOIN public.financial_agreements fa ON fa.id = lo.financial_agreements_id
                    LEFT JOIN public.bankers b ON b.id = fa.banker_id
                    LEFT JOIN public.proposal_wallet pw ON pw.proposal_id = p.id
                    LEFT JOIN public.proposal_benefit pb ON pb.proposal_id = p.id
                    LEFT JOIN public.benefit bt ON bt.id = pb.benefit_id
                WHERE p.is_deleted = false AND p.id = {id}
                ORDER BY p.created_at
            )
            SELECT 
                *
            FROM get_proposal;
        """
        return query