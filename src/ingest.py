"""CLI for document ingestion into the vector store and knowledge graph."""

from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    def load_dotenv() -> None:
        return None

from config import get_settings
from .app_service import GraphRAGService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ingest documents into the GraphRAG pipeline.")
    parser.add_argument("--data-dir", help="Directory containing local documents to ingest.")
    parser.add_argument(
        "--dataset-name",
        help="Hugging Face dataset name to ingest, for example zeroshot/cybersecurity-corpus.",
    )
    parser.add_argument(
        "--dataset-split",
        default=None,
        help="Dataset split to ingest. Defaults to the configured value.",
    )
    parser.add_argument(
        "--dataset-text-field",
        default=None,
        help="Optional dataset text field override.",
    )
    parser.add_argument(
        "--dataset-limit",
        type=int,
        default=None,
        help="Optional record limit when ingesting from a dataset source.",
    )
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

    runtime_settings = settings
    if chunk_size != settings.chunk_size or chunk_overlap != settings.chunk_overlap:
        runtime_settings = replace(
            settings,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    service = GraphRAGService(runtime_settings)
    if args.data_dir:
        count = service.ingest_directory(Path(args.data_dir))
        print(f"Ingested {count} chunks from {args.data_dir}")
    elif args.dataset_name or runtime_settings.dataset_name:
        dataset_name = args.dataset_name or runtime_settings.dataset_name
        count = service.ingest_hf_dataset(
            dataset_name=dataset_name,
            split=args.dataset_split,
            text_field=args.dataset_text_field,
            limit=args.dataset_limit,
        )
        print(f"Ingested {count} chunks from dataset {dataset_name}")
    else:
        parser.error("Provide either --data-dir or --dataset-name.")
    service.close()

    print(f"Vector store saved to {settings.vector_store_path}")
    print(f"Document metadata saved to {settings.document_store_path}")


if __name__ == "__main__":
    main()
