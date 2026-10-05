from pathlib import Path
from pypdf import PdfReader

class DocumentLoader:

    @staticmethod
    def load(file_path: str) -> str:
        """
        Load a PDF document and return its text content.

        Args:
            file_path (str): The path to the PDF file.  
        """
        path = Path(file_path)
        #if not path.is_file() or path.suffix.lower() != ".pdf" or path.suffix.lower() != ".txt":
        #    raise ValueError(f"Invalid file path: {file_path}")
        extension = path.suffix.lower()

        if extension == ".txt":
            return DocumentLoader._load_text(path)

        if extension == ".pdf":
            return DocumentLoader._load_pdf(path)

        raise ValueError(f"Unsupported file extension: {extension}")

    @staticmethod
    def _load_text(path: Path) -> str:
        return path.read_text(
            encoding="utf-8"
        )

    @staticmethod
    def _load_pdf(path: Path) -> str:
        reader = PdfReader(str(path))
        pages = []

        for page in reader.pages:
            text = page.extract_text()

            if text:
                pages.append(text)

        return "\n".join(pages)
