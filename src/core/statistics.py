# src/core/statistics.py

from sqlalchemy import Float, Numeric, cast, func, select

from src.db.database import db
from src.models.models import Flag, FlagsProcessing, Proposal, ProposalLoan, ProposalStatus, TablesFinance, User
from src.service.response import Response
from src.utils.log import logdb
from src.utils.metadata import Metadata
from src.utils.pagination import Pagination


class StatisticsCore:

    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.proposal_status = ProposalStatus
        self.proposal_loan = ProposalLoan
        self.user = User
        self.tables_finance = TablesFinance
        self.flags = Flag
        self.proposal = Proposal
        self.flags_processing_payments = FlagsProcessing

    def list_hold_profit_sellers(self, data: dict):
        try:
            current_page = int(data.get("current_page", 1))
            rows_per_page = int(data.get("rows_per_page", 10))

            if current_page < 1:
                current_page = 1
            if rows_per_page < 1:
                rows_per_page = 1

            pagination = Pagination().pagination(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=data.get("sort_by", ""),
                order_by=data.get("order_by", ""),
                filter_by=data.get("filter_by", ""),
                filter_value=data.get("filter_value", "")
            )

            # ====== Query principal ======
            stmt = select(
                self.user.id.label("seller_id"),
                self.user.username.label("seller"),
                self.user.role.label("role"),
                func.to_char(
                    func.round(
                        func.sum(func.coalesce(self.proposal_loan.valor_operacao, 0)).cast(Numeric),
                        2
                    ),
                    'FM"R$ "999G999G999D00'
                ).label("value_total_operations")
            ).join(
                self.proposal_loan, self.proposal_loan.user_id == self.user.id
            ).join(
                self.proposal_status,
                (self.proposal_status.proposal_id == self.proposal_loan.proposal_id) &
                (self.proposal_status.user_id == self.user.id)
            ).where(
                self.user.is_deleted == False,
                self.proposal_loan.is_deleted == False,
                self.proposal_status.is_deleted == False,
                self.proposal_status.contrato_pago == True
            ).group_by(
                self.user.id,
                self.user.username,
                self.user.role
            ).order_by(
                func.sum(func.coalesce(self.proposal_loan.valor_operacao, 0)).desc()
            ).offset(
                pagination["offset"]
            ).limit(
                pagination["limit"]
            )

            result = db.session.execute(stmt).fetchall()

            if not result:
                return Response().response(
                    status_code=404,
                    error=True,
                    message_id="list_profit_list_not_found",
                    exception="Not found",
                )

            data_result = [dict(row._mapping) for row in result]

            metadata = Pagination().metadata(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=pagination["sort_by"],
                order_by=pagination["order_by"],
                filter_by=pagination["filter_by"],
                filter_value=pagination["filter_value"],
            )

            return Response().response(
                status_code=200,
                message_id="list_profit_successful",
                data=data_result,
                metadata=metadata,
            )

        except Exception as e:
            logdb("error", message=f"Error processing loan operation. {e}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_processing_list_hold_profit_sellers",
                exception=str(e),
            )
    
    def list_ranking_sellers(self, data: dict):
        try:
            current_page = int(data.get("current_page", 1))
            rows_per_page = int(data.get("rows_per_page", 10))
            if current_page < 1:
                current_page = 1
            if rows_per_page < 1:
                rows_per_page = 1

            pagination = Pagination().pagination(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=data.get("sort_by", ""),
                order_by=data.get("order_by", ""),
                filter_by=data.get("filter_by", ""),
                filter_value=data.get("filter_value", "")
            )

            # ===== CTE list_statics =====
            list_statics_stmt = (
                select(
                    self.user.id.label("id_seller"),
                    self.proposal.id.label("id_proposal"),
                    self.user.username.label("name_seller"),
                    self.proposal.nome.label("nome_proposal"),
                    self.proposal.cpf.label("cpf_proposal"),
                    self.proposal_status.contrato_pago,
                    self.proposal_loan.valor_operacao,
                    func.round(
                        cast(self.proposal_loan.valor_operacao, Numeric) * 
                        cast(self.tables_finance.rate, Numeric) / 100,
                        2
                    ).label("valor_comissionado")
                )
                .join(self.proposal, self.user.id == self.proposal.user_id)
                .join(self.proposal_status, self.proposal_status.proposal_id == self.proposal.id)
                .join(self.proposal_loan, self.proposal_loan.proposal_id == self.proposal.id)
                .join(self.tables_finance, self.tables_finance.id == self.proposal_loan.tables_finance_id)
                .where(
                    self.user.id == self.user_id,
                    self.user.is_deleted == False,
                    self.proposal_status.contrato_pago == True,
                    self.proposal.is_deleted == False,
                    self.tables_finance.is_deleted == False
                )
                .order_by(self.proposal.id, self.proposal.created_at.asc())
            ).cte("list_statics")

            # ===== CTE flags_sellers =====
            flags_sellers_stmt = (
                select(
                    self.flags_processing_payments.user_id,
                    self.flags.name,
                    self.flags.rate,
                    self.user.username.label("sellers")
                )
                .join(self.flags, self.flags.id == self.flags_processing_payments.flag_id)
                .join(self.user, self.user.id == self.flags_processing_payments.user_id)
                .where(
                    self.user.id == self.user_id,
                    self.user.is_deleted == False,
                    self.flags_processing_payments.user_id == self.user_id
                )
            ).cte("flags_sellers")

            # ===== Select final =====
            stmt = (
                select(
                    func.initcap(func.trim(list_statics_stmt.c.name_seller)).label("name_seller"),
                    func.initcap(func.trim(list_statics_stmt.c.nome_proposal)).label("nome_proposal"),
                    list_statics_stmt.c.cpf_proposal,
                    list_statics_stmt.c.contrato_pago,
                    list_statics_stmt.c.valor_operacao,
                    cast(
                        func.round(
                            cast(
                                list_statics_stmt.c.valor_comissionado * cast(flags_sellers_stmt.c.rate, Numeric) / 100,
                                Numeric
                            ),
                            2
                        ),
                        Float
                    ).label("ganho_esperado")
                )
                .join(flags_sellers_stmt, list_statics_stmt.c.id_seller == flags_sellers_stmt.c.user_id)
                .offset(pagination["offset"])
                .limit(pagination["limit"])
            )

            result = db.session.execute(stmt).fetchall()

            if not result:
                return Response().response(
                    status_code=404,
                    error=True,
                    message_id="list_ranking_sellers_not_found",
                    exception="Not found",
                )

            metadata = Pagination().metadata(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=pagination["sort_by"],
                order_by=pagination["order_by"],
                filter_by=pagination["filter_by"],
                filter_value=pagination["filter_value"]
            )

            return Response().response(
                status_code=200,
                error=False,
                message_id="list_ranking_sellers_successful",
                data=Metadata(result).model_to_list(),
                metadata=metadata
            )

        except Exception as e:
            logdb("error", message=f"Error processing list_ranking_sellers. {e}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_processing_list_ranking_sellers",
                exception=str(e),
            )