import os
from flask import url_for
from src.models.proposal import SellerModels
from src.service.response import Response
from src.utils.log import setup_logger
from src.utils.pagination import Pagination
from src.db.pg import PgAdmin
from werkzeug.datastructures import FileStorage
from src.utils.processor import ProposalProcessor
from uuid import uuid4
from werkzeug.utils import secure_filename

logger = setup_logger(__name__)


class SellerCore:

    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.models = SellerModels(user_id=user_id)
        self.pg = PgAdmin()
        self.processor = ProposalProcessor()

    def list_proposal(self, data: dict):
        current_page, rows_per_page = int(data.get("current_page", 1)), int(data.get("rows_per_page", 10))

        if current_page < 1:  # Force variables min values
            current_page = 1
        if rows_per_page < 1:
            rows_per_page = 1

        pagination = Pagination().pagination(current_page=current_page, rows_per_page=rows_per_page, sort_by=data.get("sort_by", ""), order_by=data.get("order_by", ""), filter_by=data.get("filter_by", ""))

        proposal = self.pg.fetch_to_dict(query=self.models.list_proposal(pagination=pagination))

        if not proposal:
            logger.warning(f"Proposal List Not Found.")
            return Response().response(status_code=404, error=True, message_id="proposal_list_not_found", exception="Not found", data=proposal)

        metadata = Pagination().metadata(current_page=current_page, rows_per_page=rows_per_page, sort_by=pagination["sort_by"], order_by=pagination["order_by"], filter_by=pagination["filter_by"])
        return Response().response(status_code=200, message_id="proposal_list_bankers_successful", data=proposal, metadata=metadata)

    def add_proposal(self, data, image_data: FileStorage):
        from src.external import ProposalDispatcher

        try:
            data_dict = data.to_dict(flat=True)
            image_data = image_data.to_dict(flat=False)

            if not data_dict.get("cpf"):
                logger.warning("cpf_is_required")
                return Response().response(
                    status_code=400, error=True, message_id="cpf_is_required"
                )

            proposal = self.pg.fetch_to_dict(
                query=self.models.add_proposal(data=data_dict)
            )
            self.pg.commit()

            if proposal:
                processed_images = self.processor.process_file(image_data=image_data)

                self.pg.execute_query(
                    query=self.models.proposal_image(image_files=processed_images, proposal_id=proposal[0]["id"])
                )
                self.pg.execute_query(
                    query=self.models.proposal_benefit(benefit_id=data_dict.get("benefit_id"), proposal_id=proposal[0]["id"])
                )
                self.pg.execute_query(
                    query=self.models.status_proposal(proposal_id=proposal[0]["id"])
                )
                self.pg.execute_query(
                    query=self.models.proposal_wallet(data=data, proposal_id=proposal[0]["id"])
                )
                self.pg.execute_query(
                    query=self.models.proposal_loan(data=data, proposal_id=proposal[0]["id"])
                )
                self.pg.commit()

                ProposalDispatcher.dispatch_proposal_addition(user_id=self.user_id)
                ProposalDispatcher.dispatch_proposal_count_addtion(user_id=self.user_id)

            return Response().response(
                status_code=200, error=False,
                message_id="proposal_add_successful",
                data={"id": proposal[0]["id"]}
            )

        except Exception as e:
            logger.warning(f"Error Processing Proposal {e}", exc_info=True)
            return Response().response(
                status_code=400, error=True,
                message_id="error_in_add_proposal",
                exception=str(e)
            )

    def get_proposal(self, id: int):
        try:
            proposal = self.pg.fetch_to_dict(query=self.models.get_proposal(id=id))
            if not proposal:
                logger.warning("Proposal Not Found")
                return Response().response(status_code=404, error=True, message_id="proposal_not_found", exception="Not Found")

            image_directory = os.path.join(os.getcwd(), "src", "static", "uploads")
            os.makedirs(image_directory, exist_ok=True)

            fields_with_images = ['extrato_consignacoes', 'contracheque', 'rg_cnh_completo', 'rg_frente', 'rg_verso', 'comprovante_residencia', 'comprovante_bancario', 'detalhamento_inss', 'historico_consignacoes_inss', 'selfie']

            for item in proposal:
                seller_name = secure_filename(proposal[0]['name_seller'])
                seller_directory = os.path.join(image_directory, seller_name)
                os.makedirs(seller_directory, exist_ok=True)

                for field in fields_with_images:
                    if item.get(field):
                        try:
                            image_data = bytes(item[field])  # Converte <memory> para bytes

                            unique_id = uuid4().hex
                            filename = secure_filename(f"{field}_{id}_{unique_id}.jpg")
                            file_path = os.path.join(seller_directory, filename)

                            with open(file_path, 'wb') as f:
                                f.write(image_data)

                            item[field] = url_for('static', filename=f"uploads/{seller_name}/{filename}", _external=True)
                        except Exception as save_error:
                            logger.error(f"Failed to save file for field {field}: {save_error}", exc_info=True)
                            item[field] = None
                    else:
                        item[field] = None

            for item in proposal:
                for key, value in item.items():
                    if isinstance(value, memoryview):
                        item[key] = None

            return Response().response(status_code=200, error=False, message_id="proposal_get_successful", data=proposal)
        except Exception as e:
            logger.error(f"Error processing get proposal filter by id {e}", exc_info=True)
            return Response().response(status_code=400, error=True, message_id="error_in_get_proposal", exception=str(e))

    def update_proposal(self, data, image: FileStorage, proposal_id: int):
        try:
            data_dict = data.to_dict(flat=True)
            image_data = image.to_dict(flat=False)
            processed_images = self.processor.process_file(image_data=image_data)

            query, params = self.models.update_proposal(image_files=processed_images, proposal_id=proposal_id, data=data_dict)
            self.pg.execute_query(query=query, params=params)
            self.pg.commit()
            return Response().response(status_code=200, error=False, message_id="proposal_edit_successful")

        except Exception as e:
            logger.warning(f"Error Processing Proposal Edit {e}", exc_info=True)
            return Response().response(status_code=400, error=True, message_id="proposal_edit_failed", exception=str(e))

    def delete_proposal(self, proposal_id: int):
        self.pg.execute_query(query=self.models.delete_proposal(proposal_id=proposal_id))
        self.pg.commit()
        return Response().response(status_code=200, error=False, message_id="proposal_delete_successful")