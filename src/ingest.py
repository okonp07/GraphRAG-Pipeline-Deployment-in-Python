"""CLI for document ingestion into the vector store and knowledge graph."""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    def load_dotenv() -> None:
        return None

from config import get_settings
from .knowledge_graph import KnowledgeGraph
from .utils import load_documents, save_json
from .vector_store import VectorStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ingest documents into the GraphRAG pipeline.")
    parser.add_argument("--data-dir", required=True, help="Directory containing .txt, .md, or .json documents.")
    parser.add_argument("--chunk-size", type=int, default=None, help="Chunk size in words.")
    parser.add_argument("--chunk-overlap", type=int, default=None, help="Overlap in words between chunks.")
    return parser


def main() -> None:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args()

    settings = get_settings()
    chunk_size = args.chunk_size or settings.chunk_size
    chunk_overlap = args.chunk_overlap or settings.chunk_overlap

    documents = load_documents(Path(args.data_dir), chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    vector_store = VectorStore(
        embedding_model=settings.embedding_model,
        embedding_dim=settings.embedding_dim,
        storage_path=settings.vector_store_path,
    )
    vector_store.add_documents(documents)
    vector_store.save()

    graph = KnowledgeGraph(
        uri=settings.neo4j_uri,
        username=settings.neo4j_username,
        password=settings.neo4j_password,
        database=settings.neo4j_database,
        enabled=settings.use_neo4j,
    )
    graph.clear()
    graph.ingest_documents(documents)
    graph.close()

    save_json(settings.document_store_path, documents)

    print(f"Ingested {len(documents)} chunks from {args.data_dir}")
    print(f"Vector store saved to {settings.vector_store_path}")
    print(f"Document metadata saved to {settings.document_store_path}")


if __name__ == "__main__":
    main()
