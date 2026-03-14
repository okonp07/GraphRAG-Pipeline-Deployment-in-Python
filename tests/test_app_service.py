from pathlib import Path

from config import Settings
from src.app_service import GraphRAGService


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
