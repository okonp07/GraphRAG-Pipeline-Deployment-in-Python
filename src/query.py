"""CLI for querying the hybrid GraphRAG pipeline."""

from __future__ import annotations

import argparse

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    def load_dotenv() -> None:
        return None

from config import get_settings
from .app_service import GraphRAGService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Query the GraphRAG pipeline.")
    parser.add_argument("--query", required=True, help="Natural language query to run.")
    parser.add_argument("--graph-weight", type=float, default=None, help="Weight applied to graph results.")
    parser.add_argument("--vector-weight", type=float, default=None, help="Weight applied to vector results.")
    parser.add_argument("--top-k", type=int, default=None, help="Number of results to return.")
    return parser


def main() -> None:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args()
    settings = get_settings()

    service = GraphRAGService.from_settings(settings)
    service.configure_weights(
        graph_weight=args.graph_weight if args.graph_weight is not None else settings.graph_weight,
        vector_weight=args.vector_weight if args.vector_weight is not None else settings.vector_weight,
    )
    response = service.ask(args.query, top_k=args.top_k or settings.top_k)
    results = response["results"]
    if not results:
        print("No results found. Run ingestion first or check your query.")
        service.close()
        return

    print("Answer")
    print(response["answer"])
    print(f"Confidence: {response['confidence']}")
    print("-" * 40)

    for index, result in enumerate(results, start=1):
        print(f"Result {index}")
        print(f"Document ID: {result['id']}")
        print(f"Combined score: {result['combined_score']:.4f}")
        print(f"Sources: {', '.join(result['retrieval_sources'])}")
        if result.get("matched_entities"):
            print(f"Matched entities: {', '.join(result['matched_entities'])}")
        print(f"Source path: {result.get('source_path', 'unknown')}")
        print(f"Text: {result['text'][:300]}")
        print("-" * 40)

    service.close()


if __name__ == "__main__":
    main()
