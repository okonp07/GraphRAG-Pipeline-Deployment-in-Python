from src.knowledge_graph import KnowledgeGraph


def test_knowledge_graph_indexes_entities():
    graph = KnowledgeGraph(enabled=False)
    graph.clear()
    graph.ingest_documents(
        [
            {
                "id": "doc-1",
                "text": "Phishing campaigns often bypass weak authentication controls.",
            },
            {
                "id": "doc-2",
                "text": "Encryption can limit breach impact.",
            },
        ]
    )

    results = graph.search("How do I stop phishing with authentication?", top_k=5)
    assert results
    assert results[0]["id"] == "doc-1"
    assert "phishing" in results[0]["matched_entities"]


def test_knowledge_graph_returns_empty_for_unknown_entities():
    graph = KnowledgeGraph(enabled=False)
    graph.ingest_documents([{"id": "doc-1", "text": "firewall and encryption harden systems"}])
    assert graph.search("Tell me about gardening", top_k=5) == []
