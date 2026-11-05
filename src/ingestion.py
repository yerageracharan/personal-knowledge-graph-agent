"""Document loading utilities for text, Markdown and PDF files."""
from pathlib import Path
from pypdf import PdfReader

SUPPORTED = {".txt", ".md", ".pdf"}

def extract_text(filename: str, content: bytes) -> str:
    """Extract UTF-8 text or PDF page text from uploaded file bytes."""
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED:
        raise ValueError(f"Unsupported file type: {suffix or 'unknown'}")
    if suffix == ".pdf":
        import io
        reader = PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    return content.decode("utf-8", errors="replace").strip()
