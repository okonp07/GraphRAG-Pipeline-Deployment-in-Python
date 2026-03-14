from src.hybrid_retriever import HybridRetriever
from src.knowledge_graph import KnowledgeGraph
from src.vector_store import VectorStore


def test_hybrid_retriever_combines_vector_and_graph_scores(tmp_path):
    documents = [
        {
            "id": "doc-1",
            "text": "Ransomware can be mitigated with backups and patch management.",
            "source_path": "doc-1.txt",
            "chunk_index": 0,
        },
        {
            "id": "doc-2",
            "text": "Tomato plants need regular watering.",
            "source_path": "doc-2.txt",
            "chunk_index": 0,
        },
    ]
    store = VectorStore("missing-model", embedding_dim=64, storage_path=tmp_path / "store")
    store.add_documents(documents)

    graph = KnowledgeGraph(enabled=False)
    graph.ingest_documents(documents)

    retriever = HybridRetriever(store, graph, vector_weight=0.4, graph_weight=0.6)
    results = retriever.search("How do I protect against ransomware?", top_k=2)

    assert results[0]["id"] == "doc-1"
    assert set(results[0]["retrieval_sources"]) == {"vector", "graph"}
    assert results[0]["combined_score"] >= results[1]["combined_score"]
