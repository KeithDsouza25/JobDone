from docx import Document
import io

class DocxReader:
    def read(self, file):
        try:
            doc = Document(io.BytesIO(file.read()))
            text = []
            for paragraph in doc.paragraphs:
                text.append(paragraph.text)
            return '\n'.join(text).strip()
        except Exception as e:
            raise Exception(f"Error reading DOCX file: {str(e)}")