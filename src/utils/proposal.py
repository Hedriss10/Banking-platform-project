import os 
from datetime import datetime
from werkzeug.utils import secure_filename


class UploadProposal:
    """ UploadProposal 
        
        Recibe arguments proposal_id type str, creator_id int, image_fields type list, created_at type str
        function list_images
        function create_directory_structure
        function save_images
        
    Returns:
        _type_: controllers proposal sellers
    """


    def __init__(self, proposal_id: str, creator_id: int, image_fields: list, created_at: str):
        
        if isinstance(created_at, datetime):
            self.created_at = created_at
        elif isinstance(created_at, str):
            self.created_at = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        else:
            raise ValueError("created_at deve ser uma string ou um objeto datetime")

        self.proposal_id = proposal_id
        self.creator_id = creator_id
        self.image_fields = image_fields
        
    
    def list_images(self):
        """
            Lista os caminhos das imagens salvas no diretório da proposta com o identificador correto.
            A estrutura é: proposta/ano/mês/dia/number_contrato_{proposal_id}_digitador_{creator_id}/campo_imagem
        """
        year = self.created_at.strftime("%Y")
        month = self.created_at.strftime("%m")
        day = self.created_at.strftime("%d")
        identifier = f"number_contrato_{self.proposal_id}_digitador_{self.creator_id}"
        base_path = os.path.join('proposta', year, month, day, identifier)

        image_paths = {}
        
        for field in self.image_fields:
            field_path = os.path.join(base_path, field)

            if os.path.exists(field_path) and os.path.isdir(field_path):
                files = os.listdir(field_path)

                image_paths[field] = [
                    os.path.join(year, month, day, identifier, field, img)
                    for img in files if os.path.isfile(os.path.join(field_path, img))
                ]
            else:
                print(f"Nenhuma pasta ou arquivo encontrado para {field}")

        return image_paths

    def create_directory_structure(self):
        today = datetime.now()
        year = today.strftime("%Y")
        month = today.strftime("%m")
        day = today.strftime("%d")
        base_path = os.path.join('proposta', year, month, day, str(f"""number_contrato_{self.proposal_id}_digitador_{self.creator_id}"""))

        os.makedirs(base_path, exist_ok=True)

        paths = {}
        for field in self.image_fields:
            field_path = os.path.join(base_path, field)
            os.makedirs(field_path, exist_ok=True)
            paths[field] = field_path

        return paths

    def save_images(self, files, base_path):
        saved_paths = []
        os.makedirs(base_path, exist_ok=True)
        
        for file in files:
            if file:
                filename = secure_filename(file.filename)
                filepath = os.path.join(base_path, filename)
                file.save(filepath)
                relative_path = os.path.relpath(filepath, 'proposta')
                saved_paths.append(relative_path)
        
        return saved_paths