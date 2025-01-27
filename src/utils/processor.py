import fitz 
from PIL import Image
import io

class ProposalProcessor:
    def process_file(self, image_data):
        processed_files = {}

        for field, files in image_data.items():
            for file in files:
                file_content = file.stream.read()
                if file.mimetype == "application/pdf":
                    # Processar PDF e converter em imagens
                    processed_files[field] = self.process_pdf(file_content)
                else:
                    # Validar imagem diretamente
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
                return image_stream
        except Exception as e:
            raise ValueError(f"Invalid image file: {e}")