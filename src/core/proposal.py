import os
from flask import url_for
from src.models.proposal import SellerModels
from src.service.response import Response
from src.utils.log import setup_logger
from src.utils.processor import UploadProposal
from src.utils.pagination import Pagination
from src.db.pg import PgAdmin
from werkzeug.datastructures import FileStorage
from datetime import datetime
from uuid import uuid4
from werkzeug.utils import secure_filename

logger = setup_logger(__name__)


FIELDS_WITH_IMAGES = [
    'extrato_consignacoes', 'contracheque', 'rg_cnh_completo', 'rg_frente', 
    'rg_verso', 'comprovante_residencia', 'comprovante_bancario', 
    'detalhamento_inss', 'historico_consignacoes_inss', 'selfie'
]


class SellerCore:

    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.models = SellerModels(user_id=user_id)
        self.pg = PgAdmin()

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
        try:
            data_dict = data.to_dict(flat=True)
            image_data = image_data.to_dict(flat=False)

            if not data_dict.get("cpf"):
                logger.warning("cpf_is_required")
                return Response().response(status_code=400, error=True, message_id="cpf_is_required")

            proposal = self.pg.fetch_to_dict(query=self.models.add_proposal(data=data_dict))
            self.pg.commit()

            if proposal:
                self.pg.execute_query(query=self.models.proposal_benefit(benefit_id=data_dict.get("benefit_id"), proposal_id=proposal[0]["id"]))
                self.pg.execute_query(query=self.models.status_proposal(proposal_id=proposal[0]["id"]))
                self.pg.execute_query(query=self.models.proposal_wallet(data=data, proposal_id=proposal[0]["id"]))
                self.pg.execute_query(query=self.models.proposal_loan(data=data, proposal_id=proposal[0]["id"]))

                uploader = UploadProposal(proposal_id=proposal[0]["id"], user_id=self.user_id, image_data=image_data, created_at=datetime.now())
                uploader.process_files()
                self.pg.commit()
            return Response().response(status_code=200, error=False, message_id="proposal_add_successful", data={"id": proposal[0]["id"]})

        except Exception as e:
            print("ERRROOOOO", e)
            logger.warning(f"Error Processing Proposal {e}", exc_info=True)
            return Response().response(status_code=400, error=True, message_id="error_in_add_proposal", exception=str(e))

    def get_proposal(self, id: int):
        try:
            proposal = self.pg.fetch_to_dict(query=self.models.get_proposal(id=id))
            if not proposal:
                logger.warning("Proposal Not Found")
                return Response().response(status_code=404, error=True, message_id="proposal_not_found", exception="Not Found")

            created_at = datetime.strptime(proposal[0]['created_at'], "%d-%m-%Y %H:%M")
            proposal_id = proposal[0]['id']
            user_id = proposal[0]['id_seller']

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
                    files = [file for file in os.listdir(field_directory) if os.path.isfile(os.path.join(field_directory, file))]
                    
                    urls = []
                    for file in files:
                        image_url = url_for(
                            'static', 
                            filename=f"uploads/{year}/{month}/{day}/number_contrato_{proposal_id}_digitador_{user_id}/{field}/{file}", 
                            _external=True
                        )
                        urls.append(image_url)
                    
                    image_urls[field] = urls
                else:
                    image_urls[field] = []

            return Response().response( status_code=200,  error=False,  message_id="proposal_get_successful",  data={"proposal": proposal, "image_urls": image_urls})
        except ValueError as ve:
            logger.error(f"Error parsing date: {ve}", exc_info=True)
            return Response().response(status_code=400, error=True, message_id="date_parsing_error", exception=str(ve))
        except FileNotFoundError as fe:
            logger.error(f"Directory not found: {fe}", exc_info=True)
            return Response().response(status_code=404, error=True, message_id="directory_not_found", exception=str(fe))
        except Exception as e:
            logger.error(f"Error processing get proposal filter by id {e}", exc_info=True)
            return Response().response(status_code=500, error=True, message_id="error_in_get_proposal", exception=str(e))

    def update_proposal(self, data, image: FileStorage, proposal_id: int):
        try:
            data_dict = data.to_dict(flat=True)
            image_data = image.to_dict(flat=False) if image else None

            if image_data:
                image_data = { field: files for field, files in image_data.items() if files and all(file.filename for file in files) }

            query, params = self.models.update_proposal(proposal_id=proposal_id, data=data_dict)
            self.pg.execute_query(query=query, params=params)

            if image_data:
                uploader = UploadProposal(proposal_id=proposal_id, user_id=self.user_id, image_data=image_data, created_at=datetime.now())
                uploader.process_files()

            self.pg.commit()
            return Response().response(status_code=200, error=False, message_id="proposal_update_successful")

        except Exception as e:
            logger.warning(f"Error Processing Proposal Edit {e}", exc_info=True)
            return Response().response(status_code=400, error=True, message_id="proposal_update_failed", exception=str(e))

    def delete_proposal(self, proposal_id: int):
        self.pg.execute_query(query=self.models.delete_proposal(proposal_id=proposal_id))
        self.pg.commit()
        return Response().response(status_code=200, error=False, message_id="proposal_delete_successful")
