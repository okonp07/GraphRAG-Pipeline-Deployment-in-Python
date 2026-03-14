"""Project configuration for the GraphRAG pipeline."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    """Runtime settings loaded from environment variables."""

    chunk_size: int = int(os.getenv("GRAPHRAG_CHUNK_SIZE", "400"))
    chunk_overlap: int = int(os.getenv("GRAPHRAG_CHUNK_OVERLAP", "50"))
    embedding_model: str = os.getenv(
        "GRAPHRAG_EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2",
    )
    embedding_dim: int = int(os.getenv("GRAPHRAG_EMBEDDING_DIM", "256"))
    vector_store_path: Path = Path(
        os.getenv("GRAPHRAG_VECTOR_STORE_PATH", "artifacts/vector_store")
    )
    document_store_path: Path = Path(
        os.getenv("GRAPHRAG_DOCUMENT_STORE_PATH", "artifacts/documents.json")
    )
    neo4j_uri: str = os.getenv("NEO4J_URI", "")
    neo4j_username: str = os.getenv("NEO4J_USERNAME", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "")
    neo4j_database: str = os.getenv("NEO4J_DATABASE", "neo4j")
    graph_weight: float = float(os.getenv("GRAPHRAG_GRAPH_WEIGHT", "0.5"))
    vector_weight: float = float(os.getenv("GRAPHRAG_VECTOR_WEIGHT", "0.5"))
    top_k: int = int(os.getenv("GRAPHRAG_TOP_K", "5"))
    use_neo4j: bool = os.getenv("GRAPHRAG_USE_NEO4J", "").lower() in {
        "1",
        "true",
        "yes",
    }


def get_settings() -> Settings:
    return Settings()
