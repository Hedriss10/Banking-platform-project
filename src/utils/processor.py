import os
import io
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image
import fitz  # PyMuPDF

class UploadProposal:
    image_fields = [
        'rg_cnh_completo', 'rg_frente', 'rg_verso', 'contracheque',
        'extrato_consignacoes', 'comprovante_residencia', 'selfie',
        'comprovante_bancario', 'detalhamento_inss', 'historico_consignacoes_inss'
    ]

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
        for field in self.image_fields:
            if field in self.image_data:
                field_path = os.path.join(self.base_path, field)
                os.makedirs(field_path, exist_ok=True)

                # Remove todas as imagens ou PDFs antigos do campo apenas se houver novos arquivos para substituir
                if os.path.exists(field_path):
                    for old_file in os.listdir(field_path):
                        old_file_path = os.path.join(field_path, old_file)
                        if os.path.isfile(old_file_path):
                            os.remove(old_file_path)

                # Processa e salva os novos arquivos
                for file in self.image_data[field]:
                    if file.filename:
                        file_content = file.stream.read()
                        file.stream.seek(0)  # Resetar o ponteiro para o início
                        filename = secure_filename(file.filename)

                        if file.mimetype == "application/pdf":
                            self.save_pdf(io.BytesIO(file_content), field_path, filename)
                        elif file.mimetype.startswith('image/'):
                            self.save_image(io.BytesIO(file_content), field_path, filename)

    def save_pdf(self, pdf_stream, field_path, filename):
        # Garante que o arquivo tenha a extensão .pdf
        if not filename.lower().endswith('.pdf'):
            filename = f"{os.path.splitext(filename)[0]}.pdf"
        filepath = os.path.join(field_path, filename)
        with open(filepath, 'wb') as f:
            f.write(pdf_stream.read())
        return filepath

    def process_pdf(self, pdf_stream, field_path, filename):
        # Método mantido para compatibilidade, caso precise converter PDF em imagem no futuro
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