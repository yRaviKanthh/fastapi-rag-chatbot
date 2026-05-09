from PyPDF2 import PdfReader


def load_text(file_path: str):

    if file_path.endswith(".txt"):

        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    elif file_path.endswith(".pdf"):

        reader = PdfReader(file_path)

        text = ""

        for page in reader.pages:
            text += page.extract_text()

        return text

    else:
        return "Unsupported file format"