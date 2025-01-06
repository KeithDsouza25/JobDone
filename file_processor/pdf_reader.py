import PyPDF2
import io

class PDFReader:
    def read(self, file):
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading PDF file: {str(e)}")