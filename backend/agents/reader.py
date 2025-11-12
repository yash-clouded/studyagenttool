# reader.py
from utils.pdf_utils import extract_text_from_file
from langchain_text_splitters import RecursiveCharacterTextSplitter

class ReaderAgent:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

    def read_file(self, path: str):
        """
        Read and process any supported file format (PDF, PPTX, DOCX, TXT, Images).
        Returns chunked text content.
        """
        raw = extract_text_from_file(path)
        cleaned = self.clean_text(raw)
        chunks = self.splitter.split_text(cleaned)
        return chunks

    def read_pdf(self, path: str):
        """Legacy method - redirects to read_file for backward compatibility."""
        return self.read_file(path)

    def clean_text(self, text: str) -> str:
        """Clean and normalize text from any source."""
        # Handle various line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Remove excessive whitespace
        lines = text.split("\n")
        lines = [line.strip() for line in lines]
        # Remove empty lines but keep structure
        text = "\n".join(lines)
        return text
