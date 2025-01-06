import io

class TextReader:
    def read(self, file):
        try:
            text = file.read().decode('utf-8')
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading text file: {str(e)}")