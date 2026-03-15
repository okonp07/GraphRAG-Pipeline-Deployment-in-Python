"""Utility helpers for ingestion, chunking, and cybersecurity entity extraction."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List

try:
    from pypdf import PdfReader  # type: ignore
except ImportError:  # pragma: no cover
    PdfReader = None


SUPPORTED_EXTENSIONS = {".txt", ".md", ".markdown", ".json", ".html", ".htm", ".pdf"}

CYBERSECURITY_TERMS = {
    "malware": "THREAT",
    "ransomware": "THREAT",
    "spyware": "THREAT",
    "trojan": "THREAT",
    "worm": "THREAT",
    "phishing": "ATTACK_VECTOR",
    "spear phishing": "ATTACK_VECTOR",
    "business email compromise": "ATTACK_VECTOR",
    "vulnerability": "VULNERABILITY",
    "exploit": "ATTACK_TECHNIQUE",
    "cve": "VULNERABILITY",
    "ddos": "ATTACK_TECHNIQUE",
    "botnet": "ATTACK_TECHNIQUE",
    "brute force": "ATTACK_TECHNIQUE",
    "credential stuffing": "ATTACK_TECHNIQUE",
    "privilege escalation": "ATTACK_TECHNIQUE",
    "lateral movement": "ATTACK_TECHNIQUE",
    "data exfiltration": "ATTACK_TECHNIQUE",
    "firewall": "DEFENSE_MECHANISM",
    "mfa": "DEFENSE_TECHNIQUE",
    "multi-factor authentication": "DEFENSE_TECHNIQUE",
    "encryption": "DEFENSE_TECHNIQUE",
    "authentication": "DEFENSE_TECHNIQUE",
    "patch": "DEFENSE_TECHNIQUE",
    "edr": "DEFENSE_TECHNIQUE",
    "xdr": "DEFENSE_TECHNIQUE",
    "siem": "DEFENSE_TECHNIQUE",
    "zero trust": "DEFENSE_STRATEGY",
    "least privilege": "DEFENSE_STRATEGY",
    "zero-day": "VULNERABILITY",
    "breach": "THREAT",
    "intrusion": "ATTACK_TECHNIQUE",
    "mitre att&ck": "FRAMEWORK",
    "kill chain": "FRAMEWORK",
}

PATTERN_ENTITY_TYPES = {
    r"\bCVE-\d{4}-\d{4,7}\b": "VULNERABILITY",
    r"\bT\d{4}(?:\.\d{3})?\b": "ATTACK_TECHNIQUE",
    r"\b(?:\d{1,3}\.){3}\d{1,3}\b": "IP_ADDRESS",
    r"\b[a-fA-F0-9]{32}\b": "MD5",
    r"\b[a-fA-F0-9]{40}\b": "SHA1",
    r"\b[a-fA-F0-9]{64}\b": "SHA256",
    r"\b(?:[a-zA-Z0-9-]+\.)+(?:com|net|org|io|co|ai|biz|info|ru|cn)\b": "DOMAIN",
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


def _extract_html_text(raw_html: str) -> str:
    without_scripts = re.sub(
        r"<(script|style)\b[^>]*>.*?</\1>",
        " ",
        raw_html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    without_tags = re.sub(r"<[^>]+>", " ", without_scripts)
    return normalize_text(without_tags)


def _extract_pdf_text(path: Path) -> str:
    if PdfReader is None:
        raise RuntimeError(
            "PDF ingestion requires the 'pypdf' package. Install dependencies from requirements.txt."
        )
    reader = PdfReader(str(path))
    page_text = []
    for page in reader.pages:
        page_text.append(page.extract_text() or "")
    return normalize_text(" ".join(page_text))


def read_document(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return normalize_text(_extract_json_text(json.loads(path.read_text())))
    if suffix in {".html", ".htm"}:
        return _extract_html_text(path.read_text())
    if suffix == ".pdf":
        return _extract_pdf_text(path)
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
                    "document_type": path.suffix.lower().lstrip(".") or "text",
                    "chunk_index": idx,
                    "text": chunk,
                    "entities": extract_entities(chunk),
                }
            )
    return documents


def extract_entities(text: str) -> List[Dict[str, str]]:
    lowered = text.lower()
    entities = []
    seen = set()
    for term, entity_type in CYBERSECURITY_TERMS.items():
        if term in lowered:
            key = (term, entity_type)
            if key in seen:
                continue
            seen.add(key)
            entities.append({"name": term, "type": entity_type})
    for pattern, entity_type in PATTERN_ENTITY_TYPES.items():
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            value = match.group(0)
            key = (value.lower(), entity_type)
            if key in seen:
                continue
            seen.add(key)
            entities.append({"name": value, "type": entity_type})
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
