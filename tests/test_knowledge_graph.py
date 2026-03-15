from src.knowledge_graph import KnowledgeGraph
from src.utils import extract_entities


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


def test_extract_entities_detects_cybersecurity_indicators():
    entities = extract_entities(
        "Investigators linked CVE-2024-12345 to T1059 activity from 192.168.1.10 "
        "and malware.example.com with hash "
        "44d88612fea8a8f36de82e1278abb02f."
    )

    names = {entity["name"].lower(): entity["type"] for entity in entities}

    assert names["cve-2024-12345"] == "VULNERABILITY"
    assert names["t1059"] == "ATTACK_TECHNIQUE"
    assert names["192.168.1.10"] == "IP_ADDRESS"
    assert names["malware.example.com"] == "DOMAIN"
    assert names["44d88612fea8a8f36de82e1278abb02f"] == "MD5"
