import os 
from datetime import datetime
from werkzeug.utils import secure_filename


class UploadProposal:
    """_uploadimagensProposal_
        class for save image tis proposal
        
        function create_directory_structure manipulation directory 
        function save_image manipulation save imagem 
    """
    def __init__(self) -> None:
        pass 
    
    def list_images(self, proposal_id, creator_id, image_fields):
        """
        Lista os caminhos das imagens salvas no diretório da proposta.
        """
        today = datetime.now()
        year = today.strftime("%Y")
        month = today.strftime("%m")
        day = today.strftime("%d")
        base_path = os.path.join('proposta', year, month, day, f"number_contrato_{proposal_id}_Digitador_{creator_id}")

        image_paths = {}
        for field in image_fields:
            field_path = os.path.join(base_path, field)
            if os.path.exists(field_path):
                # Cria caminhos relativos para servir as imagens
                image_paths[field] = [os.path.join(year, month, day, f"number_contrato_{proposal_id}_Digitador_{creator_id}", field, img)
                                      for img in os.listdir(field_path) if os.path.isfile(os.path.join(field_path, img))]
            else:
                image_paths[field] = []

        return image_paths
    
    
    def create_directory_structure(self, proposal_id, image_fields):
        today = datetime.now()
        year = today.strftime("%Y")
        month = today.strftime("%m")
        day = today.strftime("%d")
        base_path = os.path.join('proposta', year, month, day, str(proposal_id))

        os.makedirs(base_path, exist_ok=True)

        paths = {}
        for field in image_fields:
            field_path = os.path.join(base_path, field)
            os.makedirs(field_path, exist_ok=True)
            paths[field] = field_path

        return paths

    def save_images(self, files, base_path):
        saved_paths = []
        for file in files:
            if file:
                filename = secure_filename(file.filename)
                filepath = os.path.join(base_path, filename)
                file.save(filepath)  # Salva o arquivo no caminho específico
                saved_paths.append(filepath)
        return saved_paths
