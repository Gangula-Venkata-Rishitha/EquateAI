"""Document Reader Agent - reads PDF and DOCX scientific documents."""
from pathlib import Path
from typing import Iterator

from app.agents.base import TextLine


class DocumentReaderAgent:
    """Read scientific documents (PDF, DOCX) and yield TextLine objects."""

    def read(self, file_path: Path) -> list[TextLine]:
        """Read document and return list of text lines with page and line numbers."""
        path_str = str(file_path)
        if path_str.lower().endswith(".pdf"):
            return self._read_pdf(file_path)
        if path_str.lower().endswith(".docx"):
            return self._read_docx(file_path)
        raise ValueError(f"Unsupported format: {file_path.suffix}")

    def _read_pdf(self, file_path: Path) -> list[TextLine]:
        """Extract text from PDF using PyMuPDF."""
        try:
            import fitz  # PyMuPDF
        except ImportError:
            raise ImportError("PyMuPDF (fitz) is required for PDF support. pip install PyMuPDF")

        lines: list[TextLine] = []
        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("blocks")
            line_no = 0
            for block in blocks:
                text = block[4].strip()
                if text:
                    for line in text.split("\n"):
                        line = line.strip()
                        if line:
                            line_no += 1
                            lines.append(TextLine(content=line, page=page_num + 1, line_no=line_no))
        doc.close()
        return lines

    def _read_docx(self, file_path: Path) -> list[TextLine]:
        """Extract text from DOCX using python-docx."""
        try:
            from docx import Document as DocxDocument
        except ImportError:
            raise ImportError("python-docx is required for DOCX support. pip install python-docx")

        lines: list[TextLine] = []
        doc = DocxDocument(file_path)
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                # DOCX doesn't have page numbers easily; use paragraph index as proxy
                lines.append(TextLine(content=text, page=1, line_no=len(lines) + 1))
        return lines
