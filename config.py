"""Project configuration for the GraphRAG pipeline."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _streamlit_secret(*keys: str) -> Any:
    try:
        import streamlit as st

        value: Any = st.secrets
        for key in keys:
            value = value[key]
        return value
    except Exception:
        return None


def _get_setting(env_key: str, default: Any, *secret_keys: str) -> Any:
    env_value = os.getenv(env_key)
    if env_value not in (None, ""):
        return env_value
    secret_value = _streamlit_secret(*secret_keys) if secret_keys else None
    if secret_value not in (None, ""):
        return secret_value
    return default


def _get_bool(env_key: str, default: bool, *secret_keys: str) -> bool:
    value = _get_setting(env_key, default, *secret_keys)
    if isinstance(value, bool):
        return value
    return str(value).lower() in {"1", "true", "yes", "on"}


@dataclass
class Settings:
    """Runtime settings loaded from environment variables."""

    chunk_size: int = int(_get_setting("GRAPHRAG_CHUNK_SIZE", "400", "app", "chunk_size"))
    chunk_overlap: int = int(
        _get_setting("GRAPHRAG_CHUNK_OVERLAP", "50", "app", "chunk_overlap")
    )
    embedding_model: str = _get_setting(
        "GRAPHRAG_EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2",
        "app",
        "embedding_model",
    )
    embedding_dim: int = int(
        _get_setting("GRAPHRAG_EMBEDDING_DIM", "256", "app", "embedding_dim")
    )
    dataset_name: str = _get_setting(
        "GRAPHRAG_DATASET_NAME",
        "zeroshot/cybersecurity-corpus",
        "dataset",
        "name",
    )
    dataset_split: str = _get_setting(
        "GRAPHRAG_DATASET_SPLIT",
        "train",
        "dataset",
        "split",
    )
    dataset_text_field: str = _get_setting(
        "GRAPHRAG_DATASET_TEXT_FIELD",
        "",
        "dataset",
        "text_field",
    )
    vector_store_path: Path = Path(
        _get_setting(
            "GRAPHRAG_VECTOR_STORE_PATH",
            "artifacts/vector_store",
            "storage",
            "local_vector_store_path",
        )
    )
    document_store_path: Path = Path(
        _get_setting(
            "GRAPHRAG_DOCUMENT_STORE_PATH",
            "artifacts/documents.json",
            "storage",
            "local_document_store_path",
        )
    )
    neo4j_uri: str = _get_setting("NEO4J_URI", "", "neo4j", "uri")
    neo4j_username: str = _get_setting("NEO4J_USERNAME", "neo4j", "neo4j", "username")
    neo4j_password: str = _get_setting("NEO4J_PASSWORD", "", "neo4j", "password")
    neo4j_database: str = _get_setting("NEO4J_DATABASE", "neo4j", "neo4j", "database")
    graph_weight: float = float(
        _get_setting("GRAPHRAG_GRAPH_WEIGHT", "0.5", "app", "graph_weight")
    )
    vector_weight: float = float(
        _get_setting("GRAPHRAG_VECTOR_WEIGHT", "0.5", "app", "vector_weight")
    )
    top_k: int = int(_get_setting("GRAPHRAG_TOP_K", "5", "app", "top_k"))
    use_neo4j: bool = _get_bool("GRAPHRAG_USE_NEO4J", False, "neo4j", "enabled")
    storage_backend: str = _get_setting("GRAPHRAG_STORAGE_BACKEND", "local", "storage", "backend")
    storage_bucket: str = _get_setting("GRAPHRAG_STORAGE_BUCKET", "", "storage", "bucket")
    storage_prefix: str = _get_setting(
        "GRAPHRAG_STORAGE_PREFIX",
        "graphrag/default",
        "storage",
        "prefix",
    )
    storage_region: str = _get_setting(
        "AWS_DEFAULT_REGION",
        "us-east-1",
        "storage",
        "region",
    )
    storage_endpoint_url: str = _get_setting(
        "GRAPHRAG_STORAGE_ENDPOINT_URL",
        "",
        "storage",
        "endpoint_url",
    )
    aws_access_key_id: str = _get_setting(
        "AWS_ACCESS_KEY_ID",
        "",
        "storage",
        "aws_access_key_id",
    )
    aws_secret_access_key: str = _get_setting(
        "AWS_SECRET_ACCESS_KEY",
        "",
        "storage",
        "aws_secret_access_key",
    )


def get_settings() -> Settings:
    return Settings()
