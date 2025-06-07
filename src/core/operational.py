from datetime import datetime

from sqlalchemy import case, func, literal, or_, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import aliased

from src.db.database import db
from src.models.models import (
    Bankers,
    FinancialAgreements,
    History,
    LoanOperation,
    ManageOperation,
    Proposal,
    ProposalLoan,
    ProposalStatus,
    User,
)
from src.service.response import Response
from src.utils.log import logdb
from src.utils.metadata import Metadata
from src.utils.pagination import Pagination


class OperationalCore:
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.proposal = Proposal
        self.proposal_loan = ProposalLoan
        self.proposal_status = ProposalStatus
        self.user = User
        self.manage_operational = ManageOperation
        self.loan_operation = LoanOperation
        self.history = History
        self.financial_agreements = FinancialAgreements
        self.bankers = Bankers

    def check_summary_fields_proposal(self, proposal_id: int):
        # TODO - Depois colcoar o financial_agreements_id no tratamento antes de pagar a proposta...
        try:
            if not proposal_id:
                raise ValueError("Proposal ID is required")
            stmt = select(
                self.proposal_loan.prazo_inicio,
                self.proposal_loan.prazo_fim,
                self.proposal_loan.valor_operacao,
            ).where(
                self.proposal_loan.proposal_id == proposal_id,
                self.proposal_loan.is_deleted == False,
            )
            result = db.session.execute(stmt).fetchone()
            if result:
                prazo_inicio, prazo_fim, valor_operacao = result
                is_valid = all(
                    field is not None
                    for field in [prazo_inicio, prazo_fim, valor_operacao]
                )
                return is_valid
            return False

        except Exception as e:
            logdb("error", message=f"Error checking summary proposal: {e}")
            raise

    def list_proposal(self, data: dict):
        try:
            # ====== Paginação ======
            current_page = max(int(data.get("current_page", 1)), 1)
            rows_per_page = max(int(data.get("rows_per_page", 10)), 1)

            pagination = Pagination().pagination(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=data.get("sort_by", ""),
                order_by=data.get("order_by", ""),
                filter_by=data.get("filter_by", ""),
                filter_value=data.get("filter_value", ""),
            )

            # ====== CTE de status ======
            u_alias = aliased(self.user)
            status_proposal_cte = (
                select(
                    self.proposal_status.proposal_id,
                    u_alias.username.label("digitador_por"),
                    self.manage_operational.created_at.label("digitado_as"),
                    self.proposal_status.action_at.label("status_updated_at"),
                    self.proposal_status.action_by.label("status_updated_by"),
                    u_alias.username.label("status_updated_by_name"),
                    case(
                        (self.proposal_status.contrato_pago, "Contrato Pago"),
                        (
                            self.proposal_status.aguardando_digitacao,
                            "Aguardando Digitação",
                        ),
                        (
                            self.proposal_status.pendente_digitacao,
                            "Pendente de Digitação",
                        ),
                        (
                            self.proposal_status.contrato_em_digitacao,
                            "Contrato em Digitação",
                        ),
                        (
                            self.proposal_status.aguardando_pagamento,
                            "Aguardando Pagamento",
                        ),
                        (
                            self.proposal_status.aceite_feito_analise_banco,
                            "Aceite Feito - Análise Banco",
                        ),
                        (
                            self.proposal_status.contrato_pendente_banco,
                            "Contrato Pendente - Banco",
                        ),
                        (
                            self.proposal_status.contrato_reprovado,
                            "Contrato Reprovado",
                        ),
                        else_="Unknown",
                    ).label("current_status"),
                )
                .distinct(self.proposal_status.proposal_id)
                .join(
                    self.manage_operational,
                    self.manage_operational.proposal_id
                    == self.proposal_status.proposal_id,
                    isouter=True,
                )
                .join(
                    u_alias,
                    u_alias.id == self.proposal_status.action_by,
                    isouter=True,
                )
                .where(self.proposal_status.is_deleted == False)
                .order_by(
                    self.proposal_status.proposal_id,
                    self.proposal_status.created_at.desc(),
                )
                .cte("status_proposal")
            )

            # ====== Filtro especial por status ======
            status_filters = {
                "Contrato Pago": ["Contrato Pago"],
                "Contrato Reprovado": ["Contrato Reprovado"],
            }
            filter_by_value = data.get("filter_by")
            if filter_by_value in status_filters:
                filter_proposal = status_proposal_cte.c.current_status.in_(
                    status_filters[filter_by_value]
                )
            else:
                filter_proposal = status_proposal_cte.c.current_status.notin_(
                    ["Contrato Pago", "Contrato Reprovado"]
                )

            # ====== Query principal ======
            stmt = (
                select(
                    self.proposal.id,
                    func.initcap(func.trim(self.user.username)).label(
                        "nome_digitador"
                    ),
                    func.initcap(func.trim(self.proposal.nome)).label(
                        "nome_cliente"
                    ),
                    self.proposal.cpf.label("cpf_cliente"),
                    func.to_char(
                        self.proposal.created_at, "DD-MM-YYYY HH24:MI"
                    ).label("data_criacao"),
                    status_proposal_cte.c.current_status,
                    func.initcap(func.trim(self.loan_operation.name)).label(
                        "tipo_operacao"
                    ),
                    func.upper(self.bankers.name).label("banco"),
                    func.to_char(
                        status_proposal_cte.c.digitado_as, "DD-MM-YYYY HH24:MI"
                    ).label("digitado_as"),
                    func.initcap(
                        func.trim(status_proposal_cte.c.digitador_por)
                    ).label("digitador_por"),
                )
                .join(
                    self.user,
                    self.user.id == self.proposal.user_id,
                    isouter=True,
                )
                .join(
                    self.proposal_loan,
                    self.proposal_loan.proposal_id == self.proposal.id,
                    isouter=True,
                )
                .join(
                    self.loan_operation,
                    self.loan_operation.id
                    == self.proposal_loan.loan_operation_id,
                    isouter=True,
                )
                .join(
                    self.financial_agreements,
                    self.financial_agreements.id
                    == self.proposal_loan.financial_agreements_id,
                    isouter=True,
                )
                .join(
                    self.bankers,
                    self.bankers.id == self.financial_agreements.banker_id,
                    isouter=True,
                )
                .join(
                    status_proposal_cte,
                    status_proposal_cte.c.proposal_id == self.proposal.id,
                    isouter=True,
                )
                .where(
                    self.proposal.is_deleted == False,
                    self.proposal_loan.is_deleted == False,
                    filter_proposal,
                )
            )

            # ====== Filtro dinâmico ======
            if pagination["filter_by"]:
                filter_value = f"%{pagination['filter_by']}%"
                stmt = stmt.where(
                    or_(
                        func.unaccent(self.proposal.nome).ilike(func.unaccent(filter_value)),
                        func.unaccent(self.proposal.cpf).ilike(func.unaccent(filter_value)),
                        func.unaccent(status_proposal_cte.c.current_status).ilike(func.unaccent(filter_value)),
                        func.unaccent(self.user.username).ilike(func.unaccent(filter_value)),
                        func.unaccent(status_proposal_cte.c.digitador_por).ilike(func.unaccent(filter_value)),
                    )
                )       
            # ====== Ordenação ======
            if pagination["order_by"]:
                col = getattr(self.proposal, pagination["order_by"], None)
                if col:
                    stmt = stmt.order_by(
                        col.asc()
                        if pagination["sort_by"] == "asc"
                        else col.desc()
                    )
            else:
                stmt = stmt.order_by(self.proposal.created_at.desc())

            # ====== Execução ======
            paginated_stmt = stmt.offset(pagination["offset"]).limit(
                pagination["limit"]
            )
            result = db.session.execute(paginated_stmt).fetchall()

            if not result:
                return Response().response(
                    status_code=404,
                    error=True,
                    message_id="proposal_not_found",
                )

            # ====== Contagem total ======
            count_stmt = (
                select(func.count())
                .select_from(self.proposal)
                .where(self.proposal.is_deleted == False)
            )
            total = db.session.execute(count_stmt).scalar()

            metadata = Pagination().metadata(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=pagination["sort_by"],
                order_by=pagination["order_by"],
                filter_by=pagination["filter_by"],
                filter_value=pagination["filter_value"],
                total=total,
            )

            return Response().response(
                status_code=200,
                error=False,
                message_id="proposal_list_successful",
                data=Metadata(result).model_to_list(),
                metadata=metadata,
            )

        except Exception as e:
            logdb("error", message=f"Error listing proposal: {e}")
            return Response().response(
                status_code=500, error=True, message_id="error_list_proposal"
            )

    def count_proposal(self):
        try:
            stmt = (
                select(func.count())
                .select_from(self.proposal)
                .where(self.proposal.is_deleted == False)
            )

            result = db.session.execute(stmt).fetchall()

            if not result:
                return Response().response(
                    status_code=404,
                    error=True,
                    message_id="proposal_not_found",
                )

            return Response().response(
                status_code=200,
                error=False,
                message_id="count_proposal_successful",
                data=Metadata(result).model_to_list(),
            )
        except Exception as e:
            logdb("error", message=f"Error Count Proposal: {e}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_count_proposal",
                exception=str(e),
            )

    def typing_proposal(self, proposal_id: int, data: dict):
        try:
            # Validar ID da proposta
            if not proposal_id:
                return Response().response(
                    status_code=400, error=True, message_id="id_is_required"
                )

            proposal = (
                db.session.query(self.proposal)
                .filter(
                    self.proposal.id == proposal_id,
                    self.proposal.is_deleted == False,
                )
                .first()
            )
            if not proposal:
                return Response().response(
                    status_code=404,
                    error=True,
                    message_id="proposal_not_found",
                )

            # Validar campos obrigatórios se contrato_pago for True, Validar com o stack holders essa tratativa
            # if data.get("contrato_pago"):
            #     is_valid = self.check_summary_fields_proposal(proposal_id)
            #     if not is_valid:
            #         return Response().response(
            #             status_code=409,
            #             error=True,
            #             message_id="proposal_summary_fields_missing",
            #             exception="Required fields (prazo_inicio, prazo_fim, valor_operacao, financial_agreements_id) are missing",
            #         )

            # Montar dicionário de colunas para atualização
            columns_register = {
                "aguardando_digitacao": data.get("aguardando_digitacao"),
                "pendente_digitacao": data.get("pendente_digitacao"),
                "contrato_em_digitacao": data.get("contrato_em_digitacao"),
                "aceite_feito_analise_banco": data.get(
                    "aceite_feito_analise_banco"
                ),
                "contrato_pendente_banco": data.get("contrato_pendente_banco"),
                "aguardando_pagamento": data.get("aguardando_pagamento"),
                "contrato_pago": data.get("contrato_pago"),
                "contrato_reprovado": data.get("contrato_reprovado"),
                "action_at": datetime.now(),
                "action_by": self.user_id,
            }

            # Filtrar apenas campos com valores não nulos
            columns_register = {
                k: v for k, v in columns_register.items() if v is not None
            }

            # Verificar se há campos para atualizar
            if not columns_register:
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="no_fields_to_update",
                    exception="No valid status fields provided",
                )

            # Buscar ou criar registro em proposal_status
            proposal_status = (
                db.session.query(self.proposal_status)
                .filter(
                    self.proposal_status.proposal_id == proposal_id,
                    self.proposal_status.is_deleted == False,
                )
                .first()
            )

            if not proposal_status:
                # Criar novo registro
                proposal_status = self.proposal_status(
                    proposal_id=proposal_id,
                    **columns_register,
                    is_deleted=False,
                )
                db.session.add(proposal_status)
            else:
                # Atualizar registro existente
                stmt = (
                    update(self.proposal_status)
                    .where(
                        self.proposal_status.proposal_id == proposal_id,
                        self.proposal_status.is_deleted == False,
                    )
                    .values(**columns_register)
                )
                db.session.execute(stmt)

            # Inserir registro em history
            description = data.get("description", "")
            if description:
                history_stmt = insert(self.history).values(
                    proposal_id=proposal_id,
                    user_id=self.user_id,
                    description=description,
                    created_at=datetime.now(),
                )
                db.session.execute(history_stmt)

            # Gerenciar manage_operational se number_proposal for fornecido
            number_proposal = data.get("number_proposal")
            if number_proposal is not None:
                manage_op_stmt = (
                    insert(self.manage_operational)
                    .values(
                        number_proposal=number_proposal,
                        proposal_id=proposal_id,
                        created_at=datetime.now(),
                        user_id=self.user_id,
                    )
                    .on_conflict_do_update(
                        index_elements=["proposal_id"],
                        set_={
                            "number_proposal": number_proposal,
                            "created_at": datetime.now(),
                            "user_id": self.user_id,
                        },
                    )
                )
                db.session.execute(manage_op_stmt)

            # Commit da transação
            db.session.commit()

            return Response().response(
                status_code=200,
                error=False,
                message_id="proposal_typing_successful",
            )

        except Exception as e:
            db.session.rollback()
            logdb("error", message=f"Error typing proposal: {e}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_typing_proposal",
                exception=str(e),
            )

    def history_proposal(self, proposal_id: int, data: dict):
        try:
            current_page, rows_per_page = (
                int(data.get("current_page", 1)),
                int(data.get("rows_per_page", 10)),
            )

            current_page = max(current_page, 1)
            rows_per_page = max(rows_per_page, 1)

            pagination = Pagination().pagination(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=data.get("sort_by", ""),
                order_by=data.get("order_by", ""),
                filter_by=data.get("filter_by", ""),
                filter_value=data.get("filter_value", ""),
            )

            # Query principal com JOIN para proposal
            stmt = (
                select(
                    self.history.id.label("id_historico"),
                    self.user.username.label("criado_por"),
                    func.to_char(self.history.created_at, "YYYY-MM-DD").label(
                        "criado_as"
                    ),
                    func.initcap(func.trim(self.history.description)).label(
                        "descricao"
                    ),
                )
                .outerjoin(self.user, self.user.id == self.history.user_id)
                .where(self.history.proposal_id == proposal_id)
                .order_by(self.history.created_at.desc())
            )

            # ====== Ordenação ======
            if pagination["order_by"]:
                sort_column = getattr(
                    self.history, pagination["order_by"], None
                )
                if sort_column is not None:
                    if pagination["sort_by"] == "asc":
                        stmt = stmt.order_by(sort_column.asc())
                    else:
                        stmt = stmt.order_by(sort_column.desc())
            else:
                stmt = stmt.order_by(self.history.created_at.desc())

            # Paginação
            paginated_stmt = stmt.offset(pagination["offset"]).limit(
                pagination["limit"]
            )
            result = db.session.execute(paginated_stmt).fetchall()

            # Contagem de registros
            count_stmt = (
                select(func.count())
                .select_from(self.history)
                .where(self.history.proposal_id == proposal_id)
            )
            total = db.session.execute(count_stmt).scalar() or 0

            # Verificar se há resultados
            if not result:
                return Response().response(
                    status_code=404,
                    error=False,
                    message_id="history_not_found",
                )

            metadata = Pagination().metadata(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=pagination["sort_by"],
                order_by=pagination["order_by"],
                filter_by=pagination["filter_by"],
                filter_value=pagination["filter_value"],
                total=total,
            )

            return Response().response(
                status_code=200,
                error=False,
                message_id="history_proposal_successful",
                data=Metadata(result).model_to_list(),
                metadata=metadata,
            )

        except Exception as e:
            logdb("error", message=f"Error processing history proposal: {e}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_history_proposal",
                exception=str(e),
            )

    def details_proposal(self, proposal_id: int):
        try:
            if not proposal_id:
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="id_proposal_is_required",
                )

            stmt = (
                select(
                    self.proposal_status.proposal_id.label("proposal_id"),
                    self.proposal_status.aguardando_digitacao.label(
                        "aguardando_digitacao"
                    ),
                    self.proposal_status.pendente_digitacao.label(
                        "pendente_digitacao"
                    ),
                    self.proposal_status.contrato_em_digitacao.label(
                        "contrato_em_digitacao"
                    ),
                    self.proposal_status.aceite_feito_analise_banco.label(
                        "aceite_feito_analise_banco"
                    ),
                    self.proposal_status.contrato_pendente_banco.label(
                        "contrato_pendente_banco"
                    ),
                    self.proposal_status.aguardando_pagamento.label(
                        "aguardando_pagamento"
                    ),
                    self.proposal_status.contrato_pago.label("contrato_pago"),
                    self.proposal_status.contrato_reprovado.label(
                        "contrato_reprovado"
                    ),
                    self.manage_operational.number_proposal.label(
                        "number_proposal"
                    ),
                    func.coalesce(
                        func.json_agg(
                            func.json_build_object(
                                "user_description",
                                self.user.username,
                                "description",
                                func.initcap(
                                    func.trim(self.history.description)
                                ),
                                "created_at",
                                func.to_char(
                                    self.history.created_at,
                                    "YYYY-MM-DD HH24:MI:SS",
                                ),
                            )
                        ).filter(self.history.id.isnot(None)),
                        literal([]),
                    ).label("reports"),
                )
                .outerjoin(
                    self.manage_operational,
                    self.manage_operational.proposal_id
                    == self.proposal_status.proposal_id,
                )
                .outerjoin(
                    self.history,
                    self.history.proposal_id
                    == self.proposal_status.proposal_id,
                )
                .outerjoin(self.user, self.user.id == self.history.user_id)
                .where(
                    self.proposal_status.proposal_id == proposal_id,
                    self.proposal_status.is_deleted == False,
                )
                .group_by(
                    self.proposal_status.id,
                    self.manage_operational.number_proposal,
                )
            )

            result = db.session.execute(stmt).fetchall()

            if not result:
                return Response().response(
                    status_code=404,
                    error=True,
                    message_id="details_proposal_not_found",
                )

            return Response().response(
                status_code=200,
                error=False,
                message_id="details_proposal_successful",
                data=Metadata(result).model_to_list(),
            )
        except Exception as e:
            logdb("error", message=f"Error processing details proposal: {e}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_details_proposal",
                exception=str(e),
            )
