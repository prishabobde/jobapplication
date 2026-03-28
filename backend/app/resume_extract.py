"""Best-effort plain text from stored resume files."""

from pathlib import Path


def extract_resume_text(file_path: Path, max_chars: int = 14_000) -> str:
    if not file_path.is_file():
        return "[File missing on server]"
    suf = file_path.suffix.lower()
    try:
        if suf == ".txt":
            text = file_path.read_text(encoding="utf-8", errors="replace")
        elif suf == ".pdf":
            from pypdf import PdfReader

            reader = PdfReader(str(file_path))
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
        elif suf == ".docx":
            import docx

            document = docx.Document(str(file_path))
            text = "\n".join(p.text for p in document.paragraphs)
        else:
            return f"[Unsupported resume type {suf}; ask applicant to upload .txt or .pdf]"
    except Exception as exc:  # noqa: BLE001 — return diagnostic for LLM context
        return f"[Could not read resume ({suf}): {exc}]"
    text = text.strip()
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[…truncated for summarization…]"
    return text or "[No extractable text in file]"
