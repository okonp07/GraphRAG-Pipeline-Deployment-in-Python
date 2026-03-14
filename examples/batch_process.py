"""Example script for batch ingestion followed by a sample query."""

from pathlib import Path

from config import get_settings
from src.hybrid_retriever import HybridRetriever
from src.knowledge_graph import KnowledgeGraph
from src.utils import load_documents
from src.vector_store import VectorStore


def main() -> None:
    settings = get_settings()
    data_dir = Path("examples/data")
    documents = load_documents(data_dir, settings.chunk_size, settings.chunk_overlap)

    vector_store = VectorStore(
        embedding_model=settings.embedding_model,
        embedding_dim=settings.embedding_dim,
        storage_path=settings.vector_store_path,
    )
    vector_store.add_documents(documents)

    graph = KnowledgeGraph(enabled=False)
    graph.ingest_documents(documents)

    retriever = HybridRetriever(vector_store, graph, settings.vector_weight, settings.graph_weight)
    results = retriever.search("What helps defend against ransomware?", top_k=3)
    for item in results:
        print(item["id"], item["retrieval_sources"])


if __name__ == "__main__":
    main()
