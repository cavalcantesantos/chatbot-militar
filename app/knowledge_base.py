from pathlib import Path
import re
import unicodedata

BASE_DIR = Path(__file__).resolve().parent.parent
DOCUMENTS_DIR = BASE_DIR / "documents" / "fontes_oficiais"
ALLOWED_SUFFIXES = {".txt", ".md"}

def _normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.lower())
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", " ", value).strip()

def retrieve_documents(question: str, top_k: int = 3) -> list[dict]:
    """Busca lexical simples em TXT/Markdown; substituível por embeddings futuramente."""
    if not DOCUMENTS_DIR.exists():
        return []

    terms = set(_normalize(question).split())
    if not terms:
        return []

    matches = []
    for path in DOCUMENTS_DIR.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in ALLOWED_SUFFIXES:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        normalized = _normalize(content)
        score = sum(1 for term in terms if len(term) > 2 and term in normalized)
        if score:
            matches.append({
                "title": path.stem.replace("_", " ").replace("-", " ").title(),
                "content": content[:12000],
                "url": None,
                "type": "documento_local",
                "score": score,
            })

    matches.sort(key=lambda item: item["score"], reverse=True)
    return matches[:top_k]
