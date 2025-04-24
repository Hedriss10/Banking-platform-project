import os
from datetime import datetime
from decimal import Decimal

from flask import url_for
from sqlalchemy import case, func, insert, or_, select
from sqlalchemy.orm import aliased
from werkzeug.datastructures import FileStorage

from src.db.database import db
from src.models.models import (
    Bankers,
    Benefit,
    FinancialAgreements,
    LoanOperation,
    Proposal,
    ProposalBenenift,
    ProposalLoan,
    ProposalStatus,
    ProposalWallet,
    TablesFinance,
    User,
)
from src.service.response import Response
from src.utils.log import logdb
from src.utils.metadata import Metadata
from src.utils.pagination import Pagination
from src.utils.processor import UploadProposal

FIELDS_WITH_IMAGES = ['extrato_consignacoes', 'contracheque', 'rg_cnh_completo', 'rg_frente', 'rg_verso', 'comprovante_residencia', 'comprovante_bancario', 'detalhamento_inss', 'historico_consignacoes_inss', 'selfie']


class ProposalCore:
    
    def __init__(self, user_id: int, *args, **kwargs) -> None:
        self.user_id = user_id
        self.proposal = Proposal
        self.proposal_status = ProposalStatus
        self.proposal_benefit = ProposalBenenift
        self.proposal_wallet = ProposalWallet
        self.proposal_loan = ProposalLoan
        self.user = User
        self.loan_operation = LoanOperation
        self.benefit = Benefit
        self.bankers = Bankers
        self.financial_agreements = FinancialAgreements
        self.tables = TablesFinance
        
    # helpers
    def convert_value(self, value, field_type):
        if value in (None, '', ' '):
            return None
        if field_type == str:
            return value.strip()
        if field_type == Decimal:
            return Decimal(str(value).replace(',', '.'))
        if field_type == datetime:
            return datetime.strptime(value, "%d-%m-%Y %H:%M")
        if field_type == int:
            return int(value)
        raise ValueError(f"type check: {field_type}")

    def list_proposal(self, data: dict):
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
                filter_value=data.get("filter_value", ""),
            )

            # ====== CTE contract_paid_cte ======
            u_alias = aliased(self.user)

            contract_paid_cte = (select(
                self.proposal_status.proposal_id,
                case(
                    (self.proposal_status.contrato_pago, self.proposal_status.action_at),
                    (self.proposal_status.aguardando_digitacao, self.proposal_status.action_at),
                    (self.proposal_status.pendente_digitacao, self.proposal_status.action_at),
                    (self.proposal_status.contrato_em_digitacao, self.proposal_status.action_at),
                    (self.proposal_status.aceite_feito_analise_banco, self.proposal_status.action_at),
                    (self.proposal_status.contrato_pendente_banco, self.proposal_status.action_at),
                ).label("status_updated_at"),
                case(
                    (self.proposal_status.contrato_pago, self.proposal_status.action_by),
                    (self.proposal_status.aguardando_digitacao, self.proposal_status.action_by),
                    (self.proposal_status.pendente_digitacao, self.proposal_status.action_by),
                    (self.proposal_status.contrato_em_digitacao, self.proposal_status.action_by),
                    (self.proposal_status.aceite_feito_analise_banco, self.proposal_status.action_by),
                    (self.proposal_status.contrato_pendente_banco, self.proposal_status.action_by),
                ).label("status_updated_by"),
                case(
                    (self.proposal_status.contrato_pago, u_alias.username),
                    (self.proposal_status.aguardando_digitacao, u_alias.username),
                    (self.proposal_status.pendente_digitacao, u_alias.username),
                    (self.proposal_status.contrato_em_digitacao, u_alias.username),
                    (self.proposal_status.aceite_feito_analise_banco, u_alias.username),
                    (self.proposal_status.contrato_pendente_banco, u_alias.username),
                ).label("status_updated_by_name"),
                case(
                    (self.proposal_status.contrato_pago, "Contrato Pago"),
                    (self.proposal_status.aguardando_digitacao, "Aguardando Digitação"),
                    (self.proposal_status.pendente_digitacao, "Pendente de Digitação"),
                    (self.proposal_status.contrato_em_digitacao, "Contrato em Digitação"),
                    (self.proposal_status.aceite_feito_analise_banco, "Aceite Feito - Análise Banco"),
                    (self.proposal_status.contrato_pendente_banco, "Contrato Pendente - Banco"),
                ).label("current_status"),
            ).select_from(self.proposal_status).outerjoin(u_alias, u_alias.id == self.proposal_status.action_by).cte("contract_paid_cte"))

            # ====== SELECT principal ======
            cp = aliased(contract_paid_cte)

            stmt = (select(
                self.proposal.id,
                func.initcap(func.trim(self.user.username)).label("username"),
                func.initcap(func.trim(self.proposal.nome)).label("client_proposal"),
                func.to_char(self.proposal.created_at, "YYYY-MM-DD HH24:MI").label("created_at"),
                self.proposal.cpf,
                func.initcap(func.trim(self.loan_operation.name)).label("type_operation"),
                func.to_char(self.proposal.updated_at, "YYYY-MM-DD HH24:MI").label("updated_at"),
                func.initcap(func.trim(cp.c.status_updated_by_name)).label("status_updated_by_name"),
                cp.c.current_status,
            ).select_from(self.proposal)
            .outerjoin(self.user, self.user.id == self.proposal.user_id)
            .outerjoin(self.proposal_loan, self.proposal_loan.proposal_id == self.proposal.id)
            .outerjoin(self.loan_operation, self.loan_operation.id == self.proposal_loan.loan_operation_id)
            .outerjoin(cp, cp.c.proposal_id == self.proposal.id).where(
                self.proposal.is_deleted == False,
                self.user.id == self.user_id,
                self.user.is_deleted == False,
            ).group_by(
                self.proposal.id,
                self.user.username,
                self.loan_operation.name,
                cp.c.status_updated_by_name,
                cp.c.current_status,
            ))

            # ====== Filtro dinâmico se existir ======
            if pagination["filter_by"]:
                filter_value = f"%{pagination['filter_by']}%"
                stmt = stmt.where(or_(
                    func.unaccent(self.proposal.nome).ilike(func.unaccent(filter_value)),
                    func.unaccent(self.proposal.cpf).ilike(func.unaccent(filter_value)),
                ))

            # ====== Ordenação ======
            if pagination["order_by"]:
                sort_column = getattr(self.proposal, pagination["order_by"], None)
                if sort_column is not None:
                    if pagination["sort_by"] == "asc":
                        stmt = stmt.order_by(sort_column.asc())
                    else:
                        stmt = stmt.order_by(sort_column.desc())
            else:
                stmt = stmt.order_by(self.proposal.created_at.desc())

            # ====== Paginação ======
            paginated_stmt = stmt.offset(pagination["offset"]).limit(pagination["limit"])
            result = db.session.execute(paginated_stmt).fetchall()

            # ====== Total de registros respeitando o filtro ======
            count_stmt = select(func.count()).select_from(self.proposal).where(
                self.proposal.is_deleted == False,
            )

            if pagination["filter_value"]:
                count_stmt = count_stmt.where(or_(
                    func.unaccent(self.proposal.nome).ilike(func.unaccent(filter_value)),
                    func.unaccent(self.proposal.cpf).ilike(func.unaccent(filter_value)),
                ))

            total = db.session.execute(count_stmt).scalar()

            # ====== Retorno ======
            if not result:
                return Response().response(
                    status_code=404,
                    error=False,
                    message_id="proposal_not_found",
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
                message_id="proposal_list_successful",
                data=Metadata(result).model_to_list(),
                metadata=metadata,
            )

        except Exception as e:
            logdb("error", message=f"Error Processing Proposal {e}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_list_proposal",
                exception=str(e),
            )

    def add_proposal(self, data: dict, image_data: FileStorage):
        try:
            data_dict = data.to_dict(flat=True)
            image_data = image_data.to_dict(flat=False)
            new_data = {k: v for k, v in data_dict.items() if v}  # filtra valores vazios

            if not new_data.get("cpf"):
                return Response().response(
                    status_code=400, 
                    error=True, 
                    message_id="cpf_is_required"
                )

            # Pegando as colunas de cada tabela
            proposal_columns = {col.name for col in self.proposal.__table__.columns}
            wallet_columns = {col.name for col in self.proposal_wallet.__table__.columns}
            loan_columns = {col.name for col in self.proposal_loan.__table__.columns}
            benefit_columns = {col.name for col in self.proposal_benefit.__table__.columns}
            
            # Separando os dados para cada tabela
            proposal_data = {k: v for k, v in new_data.items() if k in proposal_columns}
            wallet_data = {k: v for k, v in new_data.items() if k in wallet_columns}
            loan_data = {k: v for k, v in new_data.items() if k in loan_columns}
            benefit_data = {k: v for k, v in new_data.items() if k in benefit_columns}

            # Inserir proposta principal
            proposal_stmt = insert(self.proposal).values(**proposal_data, user_id=self.user_id).returning(self.proposal.id)
            proposal_id = db.session.execute(proposal_stmt).scalar()
            db.session.commit()

            if proposal_id:
                # Inserir benefit
                if new_data.get("benefit_id"):
                    benefit_stmt = insert(self.proposal_benefit).values(
                        proposal_id=proposal_id,
                        **benefit_data
                    )
                    db.session.execute(benefit_stmt)

                # Inserir status inicial
                status_stmt = insert(self.proposal_status).values(
                    proposal_id=proposal_id,
                    user_id=self.user_id,
                    aguardando_digitacao=True,
                    pendente_digitacao=False,
                    contrato_em_digitacao=False,
                    aceite_feito_analise_banco=False,
                    contrato_pendente_banco=False,
                    aguardando_pagamento=False,
                    contrato_pago=False,
                    created_at=datetime.now(),
                )
                db.session.execute(status_stmt)

                # Inserir wallet
                wallet_stmt = insert(self.proposal_wallet).values(
                    proposal_id=proposal_id,
                    user_id=self.user_id,
                    created_at=datetime.now(),
                    **wallet_data
                )
                db.session.execute(wallet_stmt)

                # Inserir loan
                loan_stmt = insert(self.proposal_loan).values(
                    proposal_id=proposal_id,
                    user_id=self.user_id,
                    created_at=datetime.now(),
                    **loan_data
                )
                db.session.execute(loan_stmt)

                # Processar arquivos
                uploader = UploadProposal(
                    proposal_id=proposal_id,
                    user_id=self.user_id,
                    image_data=image_data,
                    created_at=datetime.now()
                )
                uploader.process_files()

                db.session.commit()

                return Response().response(
                    status_code=200,
                    error=False,
                    message_id="proposal_add_successful",
                    data={"id": proposal_id}
                )

        except Exception as e:
            db.session.rollback()
            logdb("error", message=f"Error Processing Proposal {e}")
            return Response().response(
                status_code=400,
                error=True,
                message_id="error_in_add_proposal",
                exception=str(e)
            )

    def get_proposal(self, id: int):
        try:
            if not id:
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="id_is_required"
                )

            # SELECT montado com ORM
            stmt = (
                select(
                    User.id.label("id_seller"),
                    func.initcap(func.trim(User.username)).label("name_seller"),
                    self.proposal.id,
                    func.initcap(func.trim(self.proposal.nome)).label("nome"),
                    self.proposal.genero,
                    self.proposal.email,
                    self.proposal.cpf,
                    self.proposal.rg_documento,
                    func.to_char(self.proposal.data_emissao, 'DD-MM-YYYY HH24:MI').label("data_emissao"),
                    self.proposal.naturalidade,
                    self.proposal.cidade_naturalidade,
                    self.proposal.uf_naturalidade,
                    self.proposal.orgao_emissor,
                    self.proposal.uf_emissor,
                    func.initcap(func.trim(self.proposal.nome_mae)).label("nome_mae"),
                    func.initcap(func.trim(self.proposal.nome_pai)).label("nome_pai"),
                    func.initcap(func.trim(self.proposal.bairro)).label("bairro"),
                    func.initcap(func.trim(self.proposal.endereco)).label("endereco"),
                    self.proposal.numero_endereco,
                    self.proposal.complemento_endereco,
                    func.initcap(func.trim(self.proposal.cidade)).label("cidade"),
                    self.proposal.valor_salario,
                    self.proposal.salario_liquido,
                    self.proposal.telefone,
                    self.proposal.uf_cidade,
                    self.proposal.cep,
                    func.to_char(self.proposal.data_nascimento, 'DD-MM-YYYY HH24:MI').label("data_nascimento"),
                    self.proposal.telefone_residencial,
                    self.proposal.telefone_comercial,
                    func.to_char(self.proposal.created_at, 'DD-MM-YYYY HH24:MI').label("created_at"),
                    self.proposal_loan.senha_servidor,
                    self.proposal_loan.matricula,
                    func.to_char(self.proposal_loan.data_dispacho, 'DD-MM-YYYY HH24:MI').label("data_dispacho"),
                    self.proposal_loan.margem,
                    self.proposal_loan.prazo_inicio,
                    self.proposal_loan.prazo_fim,
                    self.proposal_loan.valor_operacao,
                    func.initcap(func.trim(self.bankers.name)).label("banker_name"),
                    func.initcap(func.trim(self.financial_agreements.name)).label("name_financial_agreements"),
                    self.loan_operation.id.label("type_table"),
                    func.initcap(func.trim(self.loan_operation.name)).label("tipo_operacao"),
                    self.tables.id.label("id_tabela"),
                    self.tables.name.label("nome_tabela"),
                    self.proposal_wallet.agencia_banco,
                    self.proposal_wallet.pix_chave,
                    self.proposal_wallet.numero_conta,
                    self.proposal_wallet.agencia_dv,
                    self.proposal_wallet.agencia_op,
                    self.proposal_wallet.agency_dvop,
                    func.initcap(func.trim(self.proposal_wallet.tipo_conta)).label("tipo_conta"),
                    self.proposal_wallet.tipo_pagamento,
                    self.benefit.id.label("id_beneficio"),
                    func.initcap(func.trim(self.benefit.name)).label("tipo_beneficio"),
                )
                .join(self.user, self.proposal.user_id == self.user.id)
                .outerjoin(self.proposal_loan, self.proposal_loan.proposal_id == self.proposal.id)
                .outerjoin(self.loan_operation, self.proposal_loan.loan_operation_id == self.loan_operation.id)
                .outerjoin(self.financial_agreements, self.proposal_loan.financial_agreements_id == self.financial_agreements.id)
                .outerjoin(self.bankers, self.financial_agreements.banker_id == self.bankers.id)
                .outerjoin(self.proposal_wallet, self.proposal_wallet.proposal_id == self.proposal.id)
                .outerjoin(self.proposal_benefit, self.proposal_benefit.proposal_id == self.proposal.id)
                .outerjoin(self.benefit, self.proposal_benefit.benefit_id == self.benefit.id)
                .outerjoin(self.tables, self.proposal_loan.tables_finance_id == self.tables.id)
                .where(self.proposal.id == id, self.proposal.is_deleted == False)  # Corrigido
            )

            # Usar mappings().first() para obter um único registro
            result = db.session.execute(stmt).mappings().first()
            if not result:
                return Response().response(
                    status_code=404,
                    error=True,
                    message_id="proposal_not_found"
                )

            proposal = dict(result)
            
            # Busca de imagens
            created_at = datetime.strptime(proposal['created_at'], "%d-%m-%Y %H:%M")
            proposal_id = proposal['id']
            user_id = proposal['id_seller']

            year = created_at.strftime("%Y")
            month = created_at.strftime("%m")
            day = created_at.strftime("%d")

            base_image_directory = os.path.join(
                os.getcwd(), "src", "static", "uploads", year, month, day,
                f"number_contrato_{proposal_id}_digitador_{user_id}"
            )

            image_urls = {}
            for field in FIELDS_WITH_IMAGES:
                field_directory = os.path.join(base_image_directory, field)
                if os.path.exists(field_directory) and os.path.isdir(field_directory):
                    files = [
                        file for file in os.listdir(field_directory)
                        if os.path.isfile(os.path.join(field_directory, file))
                    ]
                    urls = [
                        url_for(
                            'static',
                            filename=f"uploads/{year}/{month}/{day}/number_contrato_{proposal_id}_digitador_{user_id}/{field}/{file}",
                            _external=True
                        )
                        for file in files
                    ]
                    image_urls[field] = urls
                else:
                    image_urls[field] = []

            return Response().response(
                status_code=200,
                error=False,
                message_id="get_proposal_sucessfully",
                data={"proposal": proposal, "image_urls": image_urls}
            )

        except Exception as e:
            logdb("error", message=f"Error Processing Proposal {e}")
            return Response().response(
                status_code=400,
                error=True,
                message_id="error_in_get_proposal",
                exception=str(e)
            )

    def update_proposal(self, proposal_id: int, data: dict, image: dict[str, list[FileStorage]] | None):
        try:
            image_data = image.to_dict(flat=False) if image else None
            if not proposal_id:
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="id_is_required"
                )

            proposal = db.session.query(self.proposal).filter(
                self.proposal.id == proposal_id,
                self.proposal.is_deleted == False
            ).first()
            if not proposal:
                return Response().response(
                    status_code=404,
                    error=True,
                    message_id="proposal_not_found"
                )

            # Definir campos permitidos e seus tipos
            tables_and_fields = {
                "proposal": {
                    "nome": str,
                    "data_nascimento": str,
                    "genero": str,
                    "email": str,
                    "cpf": str,
                    "naturalidade": str,
                    "cidade_naturalidade": str,
                    "uf_naturalidade": str,
                    "cep": str,
                    "data_emissao": str,
                    "uf_cidade": str,
                    "rg_documento": str,
                    "orgao_emissor": str,
                    "uf_emissor": str,
                    "nome_mae": str,
                    "nome_pai": str,
                    "bairro": str,
                    "endereco": str,
                    "numero_endereco": str,
                    "complemento_endereco": str,
                    "cidade": str,
                    "valor_salario": Decimal,
                    "salario_liquido": Decimal,
                    "telefone": str,
                    "telefone_residencial": str,
                    "telefone_comercial": str,
                    "observe": str,
                },
                "proposal_wallet": {
                    "agencia_banco": str,
                    "pix_chave": str,
                    "numero_conta": str,
                    "agencia_dv": str,
                    "agencia_op": str,
                    "tipo_conta": str,
                    "tipo_pagamento": str,
                },
                "proposal_loan": {
                    "senha_servidor": str,
                    "matricula": str,
                    "data_dispacho": str,
                    "margem": Decimal,
                    "prazo_inicio": int,
                    "prazo_fim": int,
                    "valor_operacao": Decimal,
                    "tables_finance_id": int,
                    "financial_agreements_id": int,
                    "loan_operation_id": int,
                },
                "proposal_benefit": {
                    "benefit_id": int,
                }
            }

            # Atualizar campos dinamicamente
            for table_name, fields in tables_and_fields.items():
                model = getattr(self, table_name)
                if table_name == "proposal":
                    instance = proposal
                    if instance:
                        for key, value in data.items():
                            if key in fields:
                                try:
                                    converted_value = self.convert_value(value, fields[key])
                                    if converted_value is not None:
                                        setattr(instance, key, converted_value)
                                except (ValueError, TypeError) as e:
                                    return Response().response(
                                        status_code=400,
                                        error=True,
                                        message_id=f"invalid_value_for_{key}",
                                        exception=str(e)
                                    )
                        setattr(instance, "updated_at", datetime.now())
                        setattr(instance, "updated_by", self.user_id)

                elif table_name == "proposal_benefit":
                    if "benefit_id" in data:
                        benefit_id = self.convert_value(data["benefit_id"], int)
                        if benefit_id:
                            benefit = db.session.query(self.benefit).filter(
                                self.benefit.id == benefit_id
                            ).first()
                            if not benefit:
                                return Response().response(
                                    status_code=400,
                                    error=True,
                                    message_id="invalid_benefit_id"
                                )

                            # Verificar se o registro já existe
                            existing = db.session.query(self.proposal_benefit).filter(
                                self.proposal_benefit.proposal_id == proposal_id,
                                self.proposal_benefit.benefit_id == benefit_id,
                                self.proposal_benefit.is_deleted == False
                            ).first()
                            if not existing:
                                new_benefit = self.proposal_benefit(
                                    proposal_id=proposal_id,
                                    benefit_id=benefit_id,
                                    updated_at=datetime.now(),
                                    updated_by=self.user_id
                                )
                                db.session.add(new_benefit)
                else:
                    instance = db.session.query(model).filter(
                        getattr(model, "proposal_id") == proposal_id
                    ).first()
                    if not instance:
                        instance = model(proposal_id=proposal_id)
                        db.session.add(instance)
                    if instance:
                        for key, value in data.items():
                            if key in fields:
                                try:
                                    converted_value = self.convert_value(value, fields[key])
                                    if converted_value is not None:
                                        setattr(instance, key, converted_value)
                                except (ValueError, TypeError) as e:
                                    return Response().response(
                                        status_code=400,
                                        error=True,
                                        message_id=f"invalid_value_for_{key}",
                                        exception=str(e)
                                    )
                        setattr(instance, "updated_at", datetime.now())
                        setattr(instance, "updated_by", self.user_id)

            if image_data:
                image_data = {field: files for field, files in image_data.items() if files and all(file.filename for file in files)}
                uploader = UploadProposal(proposal_id=proposal_id, user_id=self.user_id, image_data=image_data, created_at=datetime.now())
                uploader.process_files()

            db.session.commit()
            return Response().response(
                status_code=200,
                error=False,
                message_id="proposal_update_successful",
            )

        except Exception as e:
            db.session.rollback()
            logdb("error", message=f"Error Processing Proposal {e}")
            return Response().response(
                status_code=400,
                error=True,
                message_id="error_in_update_proposal",
                exception=str(e)
            )

    def delete_proposal(self, id: int):
        try:
            if not id:
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="id_is_required"
                )
            # soft deleted 
            self.proposal.query.filter_by(id=id).update({"is_deleted": True, "deleted_by": self.user_id, "deleted_at": datetime.now()})
            self.proposal_benefit.query.filter_by(id=id).update({"is_deleted": True, "deleted_by": self.user_id, "deleted_at": datetime.now()})
            self.proposal_loan.query.filter_by(id=id).update({"is_deleted": True, "deleted_by": self.user_id, "deleted_at": datetime.now()})
            self.proposal_status.query.filter_by(id=id).update({"is_deleted": True, "deleted_by": self.user_id, "deleted_at": datetime.now()})
            self.proposal_wallet.query.filter_by(id=id).update({"is_deleted": True, "deleted_by": self.user_id, "deleted_at": datetime.now()})

            # Commit da transação
            self.proposal.query.session.commit()
            self.proposal_benefit.query.session.commit()
            self.proposal_wallet.query.session.commit()
            self.proposal_loan.query.session.commit()
            self.proposal_status.query.session.commit()

            return Response().response(
                status_code=200,
                error=False,
                message_id="proposal_deleted_sucessfully"
            )
        except Exception as e:
            db.session.rollback()
            logdb("error", message=f"Error Processing Proposal {e}")
            return Response().response(
                status_code=400,
                error=True,
                message_id="error_in_delete_proposal",
                exception=str(e)
            )
