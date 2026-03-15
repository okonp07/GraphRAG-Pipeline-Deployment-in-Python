"""Dataset ingestion helpers for cybersecurity corpora."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

try:
    from datasets import load_dataset  # type: ignore
except ImportError:  # pragma: no cover
    load_dataset = None

from .utils import chunk_text, extract_entities, normalize_text


PREFERRED_TEXT_FIELDS = (
    "text",
    "content",
    "body",
    "description",
    "summary",
    "report",
    "article",
)


def _coerce_record_text(record: Dict[str, Any]) -> str:
    for field in PREFERRED_TEXT_FIELDS:
        value = record.get(field)
        if isinstance(value, str) and value.strip():
            return normalize_text(value)
    text_parts: List[str] = []
    for value in record.values():
        if isinstance(value, str) and value.strip():
            text_parts.append(value.strip())
    return normalize_text(" ".join(text_parts))


def _choose_source_label(dataset_name: str, split: str, record: Dict[str, Any], index: int) -> str:
    for field in ("title", "id", "name", "source", "document_id"):
        value = record.get(field)
        if value not in (None, ""):
            return f"{dataset_name}:{split}:{value}"
    return f"{dataset_name}:{split}:{index}"


def load_hf_documents(
    dataset_name: str,
    split: str,
    chunk_size: int,
    chunk_overlap: int,
    text_field: str | None = None,
    limit: int | None = None,
) -> List[Dict[str, Any]]:
    if load_dataset is None:
        raise RuntimeError(
            "Dataset ingestion requires the 'datasets' package. Install dependencies from requirements.txt."
        )
    dataset = load_dataset(dataset_name, split=split)
    documents: List[Dict[str, Any]] = []

    for record_index, record in enumerate(dataset):
        if limit is not None and record_index >= limit:
            break
        if not isinstance(record, dict):
            continue
        raw_text = ""
        if text_field:
            value = record.get(text_field)
            if isinstance(value, str):
                raw_text = normalize_text(value)
        else:
            raw_text = _coerce_record_text(record)
        if not raw_text:
            continue
        source_label = _choose_source_label(dataset_name, split, record, record_index)
        for chunk_index, chunk in enumerate(chunk_text(raw_text, chunk_size, chunk_overlap)):
            documents.append(
                {
                    "id": f"{source_label}-{chunk_index}",
                    "source_path": source_label,
                    "document_type": "dataset",
                    "chunk_index": chunk_index,
                    "text": chunk,
                    "entities": extract_entities(chunk),
                    "dataset_name": dataset_name,
                    "dataset_split": split,
                }
            )
    return documents
