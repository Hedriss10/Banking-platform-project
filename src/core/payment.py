import traceback

from sqlalchemy import BigInteger, Integer, and_, cast, func, insert, or_, outerjoin, select, update

from src.db.database import db
from src.models.models import (
    Flag,
    LoanOperation,
    ManageOperation,
    ObtianReport,
    PaymentsComission,
    Proposal,
    ProposalLoan,
    ProposalStatus,
    TablesFinance,
    User,
    Wallet,
)
from src.service.response import Response
from src.utils.log import logdb
from src.utils.metadata import Metadata
from src.utils.pagination import Pagination


class PaymentsCore:
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.report = ObtianReport
        self.proposal_loan = ProposalLoan
        self.manage_operational = ManageOperation
        self.user = User
        self.proposal_status = ProposalStatus
        self.proposal = Proposal
        self.tables_finance = TablesFinance
        self.loan_operation = LoanOperation
        self.payments_comission = PaymentsComission
        self.wallet = Wallet
        self.flag = Flag

    def __is_payment_report(self, proposal_ids: list[int]):
        try:
            subquery = (
                select(
                    self.manage_operational.number_proposal,
                    self.proposal.cpf
                )
                .select_from(
                    self.manage_operational.__table__.join(
                        self.proposal.__table__,
                        self.manage_operational.proposal_id == self.proposal.id
                    )
                )
                .where(
                    self.manage_operational.is_deleted == False,
                    self.proposal.is_deleted == False,
                    or_(
                        self.manage_operational.proposal_id.in_(proposal_ids),
                        and_(
                            self.manage_operational.number_proposal.is_(None),
                            self.proposal.id.in_(proposal_ids)
                        )
                    )
                )
            )

            results = db.session.execute(subquery).fetchall()

            number_proposals = [row.number_proposal for row in results if row.number_proposal is not None]
            cpfs = [row.cpf for row in results if row.number_proposal is None]

            if number_proposals:
                stmt = (
                    update(self.report)
                    .where(cast(self.report.number_proposal, Integer).in_(number_proposals))
                    .values(is_payment=True)
                )
                db.session.execute(stmt)

            if cpfs:
                stmt = (
                    update(self.report)
                    .where(self.report.cpf.in_(cpfs))
                    .values(is_payment=True)
                )
                db.session.execute(stmt)

            db.session.commit()

        except Exception as e:
            db.session.rollback()
            logdb("error", message=f"Error payments report. {e}\n{traceback.format_exc()}")

    def add_payment(self, data: dict) -> dict:
        try:
            payments = data.get("payments")
            if not isinstance(payments, list) or not all(
                isinstance(payment, dict) and
                all(key in payment for key in ['user_id', 'proposal_id', 'flag_id'])
                for payment in payments
            ):
                return Response.response(
                    status_code=400,
                    error=True,
                    message_id="invalid_payload_or_missing_keys"
                )

            db.session.execute(
                insert(self.payments_comission),
                [
                    {
                        'user_id': payment['user_id'],
                        'proposal_id': payment['proposal_id'],
                        'flag_id': payment['flag_id']
                    }
                    for payment in payments
                ]
            )
            # passando o numero da proposta para is_payment
            db.session.commit()
            self.__is_payment_report(proposal_ids=[p['proposal_id'] for p in payments])
            return Response().response(
                error=False,
                message_id="success_add_payment",
                status_code=200
            )
        except Exception as e:
            db.session.rollback()
            return Response().response(
                message_id="error_add_payment",
                exception=str(e),
                traceback=traceback.format_exc()
            )

    def list_proposal(self, data: dict):
        # TODO - Ajuste no `is_payment`, não está trazendo as propostas corretas
        try:
            current_page, rows_per_page = int(data.get("current_page", 1)), int(data.get("rows_per_page", 10))

            if current_page < 1:  # Force variables min values
                current_page = 1
            if rows_per_page < 1:
                rows_per_page = 1
                
            pagination = Pagination().pagination(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=data.get("sort_by", ""),
                order_by=data.get("order_by", ""),
                filter_by=data.get("filter_by", ""),
                filter_value=data.get("filter_value", ""),
            )
            stmt = select(
                self.proposal.id.label("proposal_id"),
                self.user.id.label("user_id"),
                func.upper(self.proposal.nome).label("nome"),
                func.to_char(self.proposal_loan.valor_operacao, 'FM"R$ "999G999G990D00').label("valor_operacao"),
                self.loan_operation.name.label("operacao"),
                func.upper(self.user.username).label("digitador"),
                func.upper(self.tables_finance.name).label("tabela"),
                self.tables_finance.rate
            ).outerjoin(
                self.user, self.proposal.user_id == self.user.id
            ).outerjoin(
                self.proposal_status, self.proposal_status.proposal_id == self.proposal.id
            ).outerjoin(
                self.proposal_loan, self.proposal_loan.proposal_id == self.proposal_status.proposal_id
            ).outerjoin(
                self.loan_operation, self.loan_operation.id == self.proposal_loan.loan_operation_id
            ).outerjoin(
                self.tables_finance, self.tables_finance.id == self.proposal_loan.tables_finance_id
            ).outerjoin(
                self.manage_operational, self.proposal.id == self.manage_operational.proposal_id
            ).outerjoin(
                self.report, cast(self.report.number_proposal, BigInteger) == self.manage_operational.number_proposal
            )
            
            stmt = stmt.where(
                and_(
                    self.proposal.is_deleted == False,
                    self.proposal_status.contrato_pago == True,
                    self.loan_operation.is_deleted == False,
                    self.tables_finance.is_deleted == False,
                    self.manage_operational.is_deleted == False,
                    self.report.is_deleted == False,
                    or_(
                        self.report.is_payment == False,
                        self.report.is_payment == None
                    )
                )
            )

            # ====== Filtro dinâmico se existir ======
            if pagination["filter_by"]:
                filter_value = f"%{pagination['filter_by']}%"
                stmt = stmt.where(or_(
                    func.unaccent(self.proposal.nome).ilike(func.unaccent(filter_value)),
                ))
            
            
            # ====== Paginação ======
            paginated_stmt = stmt.offset(pagination["offset"]).limit(pagination["limit"])
            result = db.session.execute(paginated_stmt).fetchall()

            if not result:
                return Response().response(
                    status_code=404,
                    error=True,
                    message_id="proposal_not_found",
                )
            
            count_stmt = select(func.count()).select_from(
                select(self.proposal.id)
                .where(self.proposal.is_deleted == False)
                .where(
                    or_(
                        func.unaccent(self.proposal.nome).ilike(func.unaccent(filter_value))
                    ) if pagination["filter_by"] else True
                ).subquery()
            )
            
            # totals
            total = db.session.execute(count_stmt).scalar()
            
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
                message_id="success_list_proposal",
                data=Metadata(result).model_to_list(),
                metadata=metadata,
            )
            
        except Exception as e:
            logdb("error", message=f"Error list proposal. {e}\n{traceback.format_exc()}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_list_proposal",
                exception=str(e),
                traceback=traceback.format_exc(e),
            )        

    def list_payments(self, data: dict):
        try:
            current_page, rows_per_page = int(data.get("current_page", 1)), int(data.get("rows_per_page", 10))
            
            if current_page < 1:  # Force variables min values
                current_page = 1
            if rows_per_page < 1:
                rows_per_page = 1
                
            pagination = Pagination().pagination(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=data.get("sort_by", ""),
                order_by=data.get("order_by", ""),
                filter_by=data.get("filter_by", ""),
                filter_value=data.get("filter_value", ""),
            )
            
            # ===== CTE de comissões com flags =====
            pc_cte = (
                select(
                    self.payments_comission.user_id,
                    self.payments_comission.proposal_id,
                    self.payments_comission.flag_id,
                    self.flag.name.label("flag_name"),
                    self.flag.rate.label("commission_rate")
                )
                .join(self.flag, self.flag.id == self.payments_comission.flag_id)
                .where(self.payments_comission.is_deleted == False, self.flag.is_deleted == False)
                .cte("payments_comission")
            )

            # ===== Query principal com cálculo da comissão =====
            stmt = (
                select(
                    func.upper(self.user.username).label("username"),
                    self.proposal.cpf,
                    self.manage_operational.number_proposal,
                    self.tables_finance.table_code,
                    self.tables_finance.rate.label("table_rate"),
                    func.to_char(self.proposal_loan.valor_operacao, 'FM"R$ "999G999G990D00').label("valor_base"),
                    pc_cte.c.commission_rate.label("taxed"),
                    func.to_char(
                        (self.proposal_loan.valor_operacao * self.tables_finance.rate / 100.0) * (pc_cte.c.commission_rate / 100.0), 'FM"R$ "999G999G990D00'
                    ).label("valor_comissao")
                )
                .select_from(self.proposal)
                .join(self.user, self.user.id == self.proposal.user_id)
                .join(self.manage_operational, self.manage_operational.proposal_id == self.proposal.id)
                .join(self.proposal_status, self.proposal_status.proposal_id == self.proposal.id)
                .join(self.proposal_loan, self.proposal_loan.proposal_id == self.proposal.id)
                .join(self.tables_finance, self.tables_finance.id == self.proposal_loan.tables_finance_id)
                .join(pc_cte, pc_cte.c.proposal_id == self.proposal.id)
                .where(
                    self.proposal.is_deleted == False,
                    self.user.is_deleted == False,
                    self.proposal_status.contrato_pago == True,
                    self.tables_finance.is_deleted == False,
                    self.proposal_loan.is_deleted == False
                )
            )
            
            # ====== Filtro dinâmico se existir ======
            if pagination["filter_by"]:
                filter_value = f"%{pagination['filter_by']}%"
                stmt = stmt.where(or_(
                    func.unaccent(self.proposal.cpf).ilike(func.unaccent(filter_value)),
                ))

            # ====== Paginação ======
            paginated_stmt = stmt.offset(pagination["offset"]).limit(pagination["limit"])
            result = db.session.execute(paginated_stmt).fetchall()

            if not result:
                return Response().response(
                    status_code=404,
                    error=True,
                    message_id="list_payments_not_found",
                )
   
            count_stmt = select(func.count()).select_from(
                select(self.proposal.id)
                .where(self.proposal.is_deleted == False)
                .where(
                    or_(
                        func.unaccent(self.proposal.nome).ilike(func.unaccent(filter_value))
                    ) if pagination["filter_by"] else True
                ).subquery()
            )
            
            # totals
            total = db.session.execute(count_stmt).scalar()
            
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
                message_id="success_list_payments",
                data=Metadata(result).model_to_list(),
                metadata=metadata,
            )
            
        except Exception as e:
            logdb("error", message=f"Error list payments. {e}\n{traceback.format_exc()}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_list_payments",
                exception=str(e),
                traceback=traceback.format_exc(e),
            )

    def export_processing_payments(self, file_type: str):
        ...
