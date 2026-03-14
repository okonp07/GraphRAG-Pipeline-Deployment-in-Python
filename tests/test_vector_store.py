from src.vector_store import FallbackEmbedder, VectorStore


def test_fallback_embedder_is_deterministic():
    embedder = FallbackEmbedder(dimension=32)
    first = embedder.encode(["phishing defense"])
    second = embedder.encode(["phishing defense"])
    assert first.shape == (1, 32)
    assert (first == second).all()


def test_vector_store_returns_ranked_results(tmp_path):
    store = VectorStore("missing-model", embedding_dim=32, storage_path=tmp_path / "store")
    store.add_documents(
        [
            {"id": "doc-1", "text": "phishing protection with multi factor authentication"},
            {"id": "doc-2", "text": "gardening tips for tomatoes"},
        ]
    )
    results = store.search("How do I stop phishing?", top_k=2)
    assert len(results) == 2
    assert results[0]["id"] == "doc-1"


def test_vector_store_can_save_and_load(tmp_path):
    store = VectorStore("missing-model", embedding_dim=32, storage_path=tmp_path / "store")
    store.add_documents([{"id": "doc-1", "text": "ransomware mitigation with backups"}])
    store.save()

    loaded = VectorStore("missing-model", embedding_dim=32, storage_path=tmp_path / "store")
    loaded.load()
    results = loaded.search("ransomware mitigation", top_k=1)
    assert results[0]["id"] == "doc-1"
