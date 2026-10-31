from PyPDF2 import PdfReader


def load_text(file_path: str):

    if file_path.endswith(".txt"):

        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            return file.read()

    elif file_path.endswith(".pdf"):

        reader = PdfReader(file_path)

        text = ""

        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"

        return text

    else:
        raise ValueError("Unsupported file format")
