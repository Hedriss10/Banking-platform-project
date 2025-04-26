# src/core/dashboard.py

from sqlalchemy import Numeric, asc, case, desc, func, literal_column, or_, select, cast, Float

from src.db.database import db
from src.models.models import ProposalLoan, ProposalStatus, User
from src.service.response import Response
from src.utils.log import logdb
from src.utils.metadata import Metadata
from src.utils.pagination import Pagination


class DashboardCore:

    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.proposal_loan = ProposalLoan
        self.proposal_status = ProposalStatus
        self.user = User

    def sales_paid(self):
        try:
            stmt = select(
                cast(
                    func.round(
                        cast(func.sum(self.proposal_loan.valor_operacao), Numeric) / 10,
                        1
                    ),
                    Float
                ).label('value_total_operations')
            ).join(
                self.proposal_status,
                self.proposal_status.proposal_id == self.proposal_loan.proposal_id
            ).where(
                self.proposal_loan.is_deleted == False,
                self.proposal_status.contrato_pago == True
            )

            result = db.session.execute(stmt).first()

            if not result or result.value_total_operations is None:
                return Response().response(
                    status_code=404,
                    error=True,
                    message_id="sales_paid_not_found",
                )

            return Response().response(
                status_code=200,
                error=False,
                message_id="sales_paid_successful",
                data=Metadata(result).model_to_list(),  # Aqui virá tipo 26285.6
            )

        except Exception as e:
            logdb("error", message=f"Error processing Dashboard. {e}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_processs_dashboard",
                exception=str(e),
            )

    def status_proposals(self):
        try:
            status_fields = [
                'aguardando_digitacao',
                'pendente_digitacao',
                'contrato_em_digitacao',
                'aceite_feito_analise_banco',
                'contrato_pendente_banco',
                'aguardando_pagamento',
                'contrato_pago'
            ]

            columns = [
                func.sum(
                    case(
                        (getattr(self.proposal_status, field) == True, 1),
                        else_=0
                    )
                ).label(f"{field}_count")
                for field in status_fields
            ]

            stmt = select(*columns).where(self.proposal_status.is_deleted == False)
            result = db.session.execute(stmt).fetchall()

            if not result:
                return Response().response(
                    status_code=404,
                    error=True,
                    message_id="status_proposals_not_found",
                )

            return Response().response(
                status_code=200,
                error=False,
                message_id="status_proposals_successful",
                data=Metadata(result).model_to_list(),
            )

        except Exception as e:
            logdb("error", message=f"Error processing Dashboard. {e}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_processs_dashboard",
                exception=str(e),
            )
    
    def sales_paid_ranking(self, data: dict):
        try:
            current_page = int(data.get("current_page", 1))
            rows_per_page = int(data.get("rows_per_page", 10))

            pagination = Pagination().pagination(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=data.get("sort_by", ""),
                order_by=data.get("order_by", ""),
                filter_by=data.get("filter_by", ""),
                filter_value=data.get("filter_value", ""),
            )

            # Base query
            stmt = select(
                self.user.id.label('seller_id'),
                self.user.username.label('seller'),
                self.user.role.label('role'),
                func.round(
                    func.sum(func.coalesce(self.proposal_loan.valor_operacao, 0)).cast(Numeric),
                    2
                ).label('value_total_operations')
            ).join(
                self.proposal_loan,
                self.proposal_loan.user_id == self.user.id
            ).join(
                self.proposal_status,
                (self.proposal_status.proposal_id == self.proposal_loan.proposal_id) &
                (self.proposal_status.user_id == self.user.id) &
                (self.proposal_status.is_deleted == False)
            ).where(
                self.user.is_deleted == False,
                self.proposal_status.contrato_pago == True,
                self.proposal_loan.is_deleted == False
            ).group_by(
                self.user.id,
                self.user.username,
                self.user.role
            )
            
            # ====== Filtro dinâmico se existir ======
            if pagination["filter_by"]:
                filter_value = f"%{pagination['filter_by']}%"
                stmt = stmt.where(or_(
                    func.unaccent(self.user.username).ilike(func.unaccent(filter_value)),
                ))

            # ====== Ordenação dinâmica segura ======
            allowed_order_columns = ["value_total_operations", "seller", "role"]
            order_column = pagination["order_by"]
            sort_direction = pagination["sort_by"]

            if order_column in allowed_order_columns:
                col = literal_column(order_column)
                if sort_direction == "asc":
                    stmt = stmt.order_by(asc(col))
                else:
                    stmt = stmt.order_by(desc(col))
            else:
                stmt = stmt.order_by(desc("value_total_operations"))

            # Paginação
            paginated_stmt = stmt.offset(pagination["offset"]).limit(pagination["limit"])
            result = db.session.execute(paginated_stmt).fetchall()

            # Contagem de registros
            count_stmt = select(func.count(self.user.id.distinct())).join(
                self.proposal_loan,
                self.proposal_loan.user_id == self.user.id
            ).join(
                self.proposal_status,
                (self.proposal_status.proposal_id == self.proposal_loan.proposal_id) &
                (self.proposal_status.user_id == self.user.id) &
                (self.proposal_status.is_deleted == False)
            ).where(
                self.user.is_deleted == False,
                self.proposal_status.contrato_pago == True,
                self.proposal_loan.is_deleted == False
            )

            total = db.session.execute(count_stmt).scalar() or 0

            if not result:
                return Response().response(
                    status_code=404,
                    error=True,
                    message_id="salles_sales_paid_ranking_not_found",
                )

            metadata = Pagination().metadata(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=pagination["sort_by"],
                order_by=pagination["order_by"],
                filter_by=pagination["filter_by"],
                filter_value=pagination["filter_value"],
                total=total
            )

            return Response().response(
                status_code=200,
                error=False,
                message_id="salles_sales_paid_ranking_successful",
                data=Metadata(result).model_to_list(),
                metadata=metadata
            )

        except Exception as e:
            logdb("error", message=f"Error processing Dashboard. {e}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_processs_dashboard",
                exception=str(e),
            )
