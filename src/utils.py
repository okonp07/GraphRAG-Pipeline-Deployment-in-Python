"""Utility helpers for ingestion, chunking, and lightweight entity extraction."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List


SUPPORTED_EXTENSIONS = {".txt", ".md", ".markdown", ".json"}

CYBERSECURITY_TERMS = {
    "malware": "THREAT",
    "ransomware": "THREAT",
    "phishing": "ATTACK_VECTOR",
    "vulnerability": "VULNERABILITY",
    "exploit": "ATTACK_TECHNIQUE",
    "cve": "VULNERABILITY",
    "ddos": "ATTACK_TECHNIQUE",
    "firewall": "DEFENSE_MECHANISM",
    "encryption": "DEFENSE_TECHNIQUE",
    "authentication": "DEFENSE_TECHNIQUE",
    "patch": "DEFENSE_TECHNIQUE",
    "zero-day": "VULNERABILITY",
    "breach": "THREAT",
    "intrusion": "ATTACK_TECHNIQUE",
}


def normalize_text(text: str) -> str:
    text = text.replace("\r", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    cleaned = normalize_text(text)
    if not cleaned:
        return []
    words = cleaned.split()
    if len(words) <= chunk_size:
        return [cleaned]

    chunks: List[str] = []
    step = max(1, chunk_size - chunk_overlap)
    for start in range(0, len(words), step):
        chunk_words = words[start : start + chunk_size]
        if not chunk_words:
            continue
        chunk = " ".join(chunk_words)
        chunks.append(chunk)
        if start + chunk_size >= len(words):
            break
    return chunks


def _extract_json_text(payload: Any) -> str:
    if isinstance(payload, str):
        return payload
    if isinstance(payload, list):
        return " ".join(_extract_json_text(item) for item in payload)
    if isinstance(payload, dict):
        preferred = []
        for key in ("text", "content", "body", "description", "summary"):
            if key in payload:
                preferred.append(_extract_json_text(payload[key]))
        if preferred:
            return " ".join(preferred)
        return " ".join(_extract_json_text(value) for value in payload.values())
    return str(payload)


def read_document(path: Path) -> str:
    if path.suffix.lower() == ".json":
        return normalize_text(_extract_json_text(json.loads(path.read_text())))
    return normalize_text(path.read_text())


def load_documents(data_dir: Path, chunk_size: int, chunk_overlap: int) -> List[Dict[str, Any]]:
    documents: List[Dict[str, Any]] = []
    data_dir = Path(data_dir)
    for path in sorted(data_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        raw_text = read_document(path)
        for idx, chunk in enumerate(chunk_text(raw_text, chunk_size, chunk_overlap)):
            documents.append(
                {
                    "id": f"{path.stem}-{idx}",
                    "source_path": str(path),
                    "chunk_index": idx,
                    "text": chunk,
                    "entities": extract_entities(chunk),
                }
            )
    return documents


def extract_entities(text: str) -> List[Dict[str, str]]:
    lowered = text.lower()
    entities = []
    for term, entity_type in CYBERSECURITY_TERMS.items():
        if term in lowered:
            entities.append({"name": term, "type": entity_type})
    return entities


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2))


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text())


def deduplicate_by_key(items: Iterable[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
    seen = set()
    deduped = []
    for item in items:
        value = item.get(key)
        if value in seen:
            continue
        seen.add(value)
        deduped.append(item)
    return deduped
