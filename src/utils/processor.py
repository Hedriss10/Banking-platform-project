import io
import os
import fitz
import shutil
from PIL import Image
from werkzeug.datastructures import FileStorage
from datetime import datetime
from werkzeug.utils import secure_filename


class ProposalProcessor:

    def process_file(self, image_data):
        processed_files = {}

        for field, files in image_data.items():
            for file in files:
                file_content = file.stream.read()
                file.stream.seek(0)  # Resetar o ponteiro para o início
                if file.mimetype == "application/pdf":
                    processed_files[field] = self.process_pdf(file_content)
                else:
                    processed_files[field] = self.validate_image(io.BytesIO(file_content))

        return processed_files

    def process_pdf(self, pdf_content):
        images = {}
        pdf_document = fitz.open(stream=pdf_content, filetype="pdf")

        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap()
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            # Validar cada página como imagem
            self.validate_image(io.BytesIO(pix.tobytes("png")))
            images[f"page_{page_num + 1}"] = io.BytesIO(pix.tobytes("png"))

        return images

    def validate_image(self, image_stream):
        try:
            with Image.open(image_stream) as img:
                img.verify()  # Verifica a integridade da imagem
                image_stream.seek(0)  # Resetar o ponteiro para o início
                return image_stream
        except Exception as e:
            raise ValueError(f"Invalid image file: {e}")


class UploadProposal:
    image_fields = ['rg_cnh_completo', 'rg_frente', 'rg_verso', 'contracheque', 'extrato_consignacoes', 'comprovante_residencia', 'selfie', 'comprovante_bancario', 'detalhamento_inss', 'historico_consignacoes_inss']

    def __init__(self, proposal_id: str, user_id: int, image_data: dict, created_at: datetime):
        self.proposal_id = proposal_id
        self.user_id = user_id
        self.image_data = image_data
        self.created_at = created_at
        self.base_path = self.create_directory_structure()

    def create_directory_structure(self):
        year = self.created_at.strftime("%Y")
        month = self.created_at.strftime("%m")
        day = self.created_at.strftime("%d")
        base_path = os.path.join("src/static/uploads", year, month, day, f"number_contrato_{self.proposal_id}_digitador_{self.user_id}")
        os.makedirs(base_path, exist_ok=True)
        return base_path

    def process_files(self):
        for field in self.image_fields:  # Itera apenas sobre os campos padronizados
            if field in self.image_data:  # Verifica se o campo foi enviado e contém arquivos válidos
                field_path = os.path.join(self.base_path, field)
                os.makedirs(field_path, exist_ok=True)

                # Remove todas as imagens antigas do campo apenas se houver novas imagens para substituir
                if os.path.exists(field_path):
                    for old_file in os.listdir(field_path):
                        old_file_path = os.path.join(field_path, old_file)
                        if os.path.isfile(old_file_path):
                            os.remove(old_file_path)

                # Processa e salva os novos arquivos
                for file in self.image_data[field]:
                    if file.filename:  # Ignora arquivos vazios
                        file_content = file.stream.read()
                        file.stream.seek(0)  # Resetar o ponteiro para o início
                        filename = secure_filename(file.filename)

                        if file.mimetype == "application/pdf":
                            self.process_pdf(io.BytesIO(file_content), field_path, filename)
                        elif file.mimetype.startswith('image/'):
                            self.save_image(io.BytesIO(file_content), field_path, filename)

    def process_pdf(self, pdf_stream, field_path, filename):
        pdf_document = fitz.open(stream=pdf_stream, filetype="pdf")
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap()
            img_stream = io.BytesIO(pix.tobytes("png"))
            page_filename = f"{filename}_page_{page_num + 1}.png"
            self.save_image(img_stream, field_path, page_filename)

    def save_image(self, image_stream, field_path, filename):
        filepath = os.path.join(field_path, filename)
        with Image.open(image_stream) as img:
            img.save(filepath)
        return filepath
