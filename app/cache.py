import hashlib
import json
from pathlib import Path

CACHE_DIR = Path(".cache")
CACHE_DIR.mkdir(exist_ok=True)

def _hash_key(*parts: str) -> str:
    raw = "||".join(parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def cache_get(*key_parts: str) -> str | None:
    """Devuelve el valor cacheado si existe, o None si no hay hit."""
    path = CACHE_DIR / f"{_hash_key(*key_parts)}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))["value"]
    return None

def cache_set(*key_parts: str, value: str) -> None:
    """Guarda el valor asociado a la combinacion de key_parts."""
    path = CACHE_DIR / f"{_hash_key(*key_parts)}.json"
    path.write_text(json.dumps({"value": value}), encoding="utf-8")