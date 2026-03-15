"""Application service layer shared by the CLI and Streamlit frontend."""

from __future__ import annotations

from pathlib import Path
from typing import List

from config import Settings
from .dataset_loader import load_hf_documents
from .generator import AnswerGenerator
from .storage import build_storage_backend
from .hybrid_retriever import HybridRetriever
from .knowledge_graph import KnowledgeGraph
from .utils import load_documents, save_json
from .vector_store import VectorStore


class GraphRAGService:
    def __init__(self, settings: Settings, storage_backend=None):
        self.settings = settings
        self.storage_backend = storage_backend or build_storage_backend(settings)
        self.vector_store = VectorStore(
            embedding_model=settings.embedding_model,
            embedding_dim=settings.embedding_dim,
            storage_path=settings.vector_store_path,
        )
        self.graph = KnowledgeGraph(
            uri=settings.neo4j_uri,
            username=settings.neo4j_username,
            password=settings.neo4j_password,
            database=settings.neo4j_database,
            enabled=settings.use_neo4j,
        )
        self.retriever = HybridRetriever(
            vector_store=self.vector_store,
            knowledge_graph=self.graph,
            vector_weight=settings.vector_weight,
            graph_weight=settings.graph_weight,
        )
        self.generator = AnswerGenerator()

    @classmethod
    def from_settings(cls, settings: Settings) -> "GraphRAGService":
        service = cls(settings)
        service.load_existing_artifacts()
        return service

    @property
    def document_count(self) -> int:
        return len(self.vector_store.metadata)

    def configure_weights(self, graph_weight: float, vector_weight: float) -> None:
        self.retriever.graph_weight = graph_weight
        self.retriever.vector_weight = vector_weight

    def reset(self) -> None:
        self.vector_store.metadata = []
        self.vector_store.index = None
        self.graph.clear()
        if self.settings.storage_backend.lower() == "s3":
            self.storage_backend.delete_prefix("vector_store")
            self.storage_backend.delete_prefix("documents")

    def ingest_directory(self, data_dir: Path) -> int:
        documents = load_documents(
            data_dir,
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
        )
        return self._ingest_documents(documents)

    def ingest_hf_dataset(
        self,
        dataset_name: str | None = None,
        split: str | None = None,
        text_field: str | None = None,
        limit: int | None = None,
    ) -> int:
        documents = load_hf_documents(
            dataset_name=dataset_name or self.settings.dataset_name,
            split=split or self.settings.dataset_split,
            text_field=text_field or self.settings.dataset_text_field or None,
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
            limit=limit,
        )
        return self._ingest_documents(documents)

    def query(self, query_text: str, top_k: int | None = None) -> List[dict]:
        return self.retriever.search(query_text, top_k=top_k or self.settings.top_k)

    def ask(self, query_text: str, top_k: int | None = None) -> dict:
        results = self.query(query_text, top_k=top_k)
        answer_payload = self.generator.generate(query_text, results)
        answer_payload["results"] = results
        return answer_payload

    def _ingest_documents(self, documents: List[dict]) -> int:
        self.reset()
        self.vector_store.add_documents(documents)
        if self.settings.storage_backend.lower() == "s3":
            self.vector_store.save_to_backend(self.storage_backend, "vector_store")
        else:
            self.vector_store.save()
        self.graph.ingest_documents(documents)
        save_json(self.settings.document_store_path, documents)
        if self.settings.storage_backend.lower() == "s3":
            self.storage_backend.upload_bytes(
                "documents/documents.json",
                self.settings.document_store_path.read_bytes(),
                content_type="application/json",
            )
        return len(documents)

    def load_existing_artifacts(self) -> None:
        if self.settings.storage_backend.lower() == "s3":
            self.vector_store.load_from_backend(self.storage_backend, "vector_store")
        else:
            self.vector_store.load()
        if self.vector_store.metadata:
            self.graph.ingest_documents(self.vector_store.metadata)

    def close(self) -> None:
        self.graph.close()
