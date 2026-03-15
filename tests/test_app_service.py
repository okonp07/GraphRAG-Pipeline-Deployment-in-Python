from pathlib import Path

from config import Settings
from src.app_service import GraphRAGService
from src.storage import MemoryStorageBackend


def test_app_service_ingests_and_queries(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "sample.txt").write_text(
        "Phishing emails can be reduced with authentication, training, and filtering."
    )

    settings = Settings(
        vector_store_path=tmp_path / "vector_store",
        document_store_path=tmp_path / "documents.json",
        use_neo4j=False,
        embedding_model="missing-model",
        embedding_dim=32,
    )
    service = GraphRAGService(settings)
    count = service.ingest_directory(data_dir)
    results = service.query("How do we reduce phishing?", top_k=1)

    assert count == 1
    assert results[0]["id"] == "sample-0"
    assert Path(settings.document_store_path).exists()

    service.close()


def test_app_service_persists_to_cloud_backend(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "sample.txt").write_text("Ransomware is reduced by backups and patching.")

    storage = MemoryStorageBackend()
    settings = Settings(
        vector_store_path=tmp_path / "vector_store",
        document_store_path=tmp_path / "documents.json",
        use_neo4j=False,
        embedding_model="missing-model",
        embedding_dim=32,
        storage_backend="s3",
        storage_bucket="demo-bucket",
    )
    service = GraphRAGService(settings, storage_backend=storage)
    service.ingest_directory(data_dir)
    service.close()

    restored = GraphRAGService(settings, storage_backend=storage)
    restored.load_existing_artifacts()
    results = restored.query("How do I reduce ransomware?", top_k=1)

    assert results[0]["id"] == "sample-0"
    restored.close()


def test_app_service_returns_grounded_answer_payload(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "sample.txt").write_text(
        "Phishing attacks can be reduced with multi-factor authentication and staff training."
    )

    settings = Settings(
        vector_store_path=tmp_path / "vector_store",
        document_store_path=tmp_path / "documents.json",
        use_neo4j=False,
        embedding_model="missing-model",
        embedding_dim=32,
    )
    service = GraphRAGService(settings)
    service.ingest_directory(data_dir)

    response = service.ask("How do I reduce phishing?", top_k=1)

    assert response["results"]
    assert response["citations"]
    assert "phishing" in response["answer"].lower()
    assert response["answer_mode"] == "fallback"

    service.close()


def test_app_service_ingests_hf_dataset(tmp_path, monkeypatch):
    sample_documents = [
        {
            "id": "dataset-doc-0",
            "source_path": "zeroshot/cybersecurity-corpus:train:doc-0",
            "document_type": "dataset",
            "chunk_index": 0,
            "text": "Ransomware impact is reduced by backups and patching.",
            "entities": [{"name": "ransomware", "type": "THREAT"}],
            "dataset_name": "zeroshot/cybersecurity-corpus",
            "dataset_split": "train",
        }
    ]

    def fake_load_hf_documents(**kwargs):
        assert kwargs["dataset_name"] == "zeroshot/cybersecurity-corpus"
        return sample_documents

    monkeypatch.setattr("src.app_service.load_hf_documents", fake_load_hf_documents)

    settings = Settings(
        vector_store_path=tmp_path / "vector_store",
        document_store_path=tmp_path / "documents.json",
        use_neo4j=False,
        embedding_model="missing-model",
        embedding_dim=32,
    )
    service = GraphRAGService(settings)

    count = service.ingest_hf_dataset(limit=10)
    results = service.query("How do I reduce ransomware?", top_k=1)

    assert count == 1
    assert results[0]["id"] == "dataset-doc-0"

    service.close()
