import io
import json
import re
from typing import List


SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".json"}


def extract_text(filename: str, content: bytes) -> str:
    ext = _extension(filename)

    if ext == ".txt":
        return content.decode("utf-8", errors="ignore").strip()

    if ext == ".json":
        data = json.loads(content.decode("utf-8", errors="ignore"))
        return json.dumps(data, ensure_ascii=False, indent=2)

    if ext == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise ValueError("PDF support requires pypdf to be installed.") from exc

        reader = PdfReader(io.BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(page.strip() for page in pages if page.strip())

    raise ValueError(f"Unsupported file type: {ext}. Supported types: .txt, .pdf, .json")


def chunk_text(text: str, min_tokens: int = 300, max_tokens: int = 500) -> List[str]:
    words = text.split()
    if not words:
        return []

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: List[str] = []
    current: List[str] = []

    for paragraph in paragraphs:
        paragraph_words = paragraph.split()
        if len(paragraph_words) > max_tokens:
            _flush(current, chunks)
            for i in range(0, len(paragraph_words), max_tokens):
                chunks.append(" ".join(paragraph_words[i:i + max_tokens]))
            continue

        if current and len(current) + len(paragraph_words) > max_tokens:
            _flush(current, chunks)

        current.extend(paragraph_words)

        if len(current) >= min_tokens:
            _flush(current, chunks)

    _flush(current, chunks)
    return chunks


def _flush(words: List[str], chunks: List[str]) -> None:
    if words:
        chunks.append(" ".join(words))
        words.clear()


def _extension(filename: str) -> str:
    dot = filename.rfind(".")
    return filename[dot:].lower() if dot >= 0 else ""
