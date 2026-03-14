"""Minimal example for querying the GraphRAG pipeline."""

from config import get_settings
from src.hybrid_retriever import HybridRetriever
from src.knowledge_graph import KnowledgeGraph
from src.vector_store import VectorStore


def main() -> None:
    settings = get_settings()
    vector_store = VectorStore(
        embedding_model=settings.embedding_model,
        embedding_dim=settings.embedding_dim,
        storage_path=settings.vector_store_path,
    )
    vector_store.load()

    graph = KnowledgeGraph(enabled=False)
    if vector_store.metadata:
        graph.ingest_documents(vector_store.metadata)

    retriever = HybridRetriever(
        vector_store=vector_store,
        knowledge_graph=graph,
        vector_weight=settings.vector_weight,
        graph_weight=settings.graph_weight,
    )
    results = retriever.search("How can I reduce phishing risk?", top_k=3)
    for item in results:
        print(item["id"], item["combined_score"], item["text"][:120])


if __name__ == "__main__":
    main()
