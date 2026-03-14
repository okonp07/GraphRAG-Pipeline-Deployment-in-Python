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
