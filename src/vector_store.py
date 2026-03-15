"""Vector store implementation with FAISS and a deterministic fallback embedder."""

from __future__ import annotations

import hashlib
import pickle
from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Dict, List, Sequence

import numpy as np

try:
    import faiss  # type: ignore
except ImportError:  # pragma: no cover
    faiss = None

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
except ImportError:  # pragma: no cover
    SentenceTransformer = None


class FallbackEmbedder:
    """A deterministic hashing embedder used when sentence-transformers is unavailable."""

    def __init__(self, dimension: int = 256):
        self.dimension = dimension

    def encode(self, texts: Sequence[str], **_: Any) -> np.ndarray:
        embeddings = np.zeros((len(texts), self.dimension), dtype="float32")
        for row, text in enumerate(texts):
            for token in text.lower().split():
                digest = hashlib.md5(token.encode("utf-8")).hexdigest()
                index = int(digest, 16) % self.dimension
                embeddings[row, index] += 1.0
            norm = np.linalg.norm(embeddings[row])
            if norm:
                embeddings[row] /= norm
        return embeddings


def build_embedder(model_name: str, fallback_dim: int = 256) -> Any:
    if SentenceTransformer is None:
        return FallbackEmbedder(dimension=fallback_dim)
    try:
        return SentenceTransformer(model_name)
    except Exception:
        return FallbackEmbedder(dimension=fallback_dim)


class NumpyIndex:
    """A small similarity index used when FAISS is not available."""

    def __init__(self, dimension: int):
        self.dimension = dimension
        self.vectors = np.zeros((0, dimension), dtype="float32")

    def add(self, vectors: np.ndarray) -> None:
        if vectors.size == 0:
            return
        self.vectors = np.vstack([self.vectors, vectors.astype("float32")])

    def search(self, queries: np.ndarray, top_k: int):
        if self.vectors.size == 0:
            distances = np.full((len(queries), top_k), np.inf, dtype="float32")
            indices = np.full((len(queries), top_k), -1, dtype="int64")
            return distances, indices
        diffs = self.vectors[None, :, :] - queries[:, None, :]
        distances = np.sum(diffs * diffs, axis=2)
        ranked = np.argsort(distances, axis=1)[:, :top_k]
        ranked_distances = np.take_along_axis(distances, ranked, axis=1)
        return ranked_distances.astype("float32"), ranked.astype("int64")


class VectorStore:
    """Embeds and stores documents for semantic search."""

    def __init__(
        self,
        embedding_model: str,
        embedding_dim: int = 256,
        storage_path: Path | str = "artifacts/vector_store",
    ):
        self.storage_path = Path(storage_path)
        self.embedder = build_embedder(embedding_model, fallback_dim=embedding_dim)
        self.embedding_dim = getattr(self.embedder, "dimension", None)
        self.metadata: List[Dict[str, Any]] = []
        self.index = None

    def _ensure_index(self, dimension: int) -> None:
        if self.index is not None:
            return
        if faiss is not None:
            self.index = faiss.IndexFlatL2(dimension)
        else:
            self.index = NumpyIndex(dimension)

    def add_documents(self, documents: Sequence[Dict[str, Any]]) -> None:
        if not documents:
            return
        texts = [doc["text"] for doc in documents]
        vectors = np.asarray(self.embedder.encode(texts), dtype="float32")
        self._ensure_index(vectors.shape[1])
        self.index.add(vectors)
        self.metadata.extend(documents)
        self.embedding_dim = vectors.shape[1]

    def search(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if self.index is None:
            return []
        query_vector = np.asarray(self.embedder.encode([query_text]), dtype="float32")
        distances, indices = self.index.search(query_vector, top_k)
        results = []
        for rank, index_value in enumerate(indices[0]):
            if index_value < 0 or index_value >= len(self.metadata):
                continue
            metadata = dict(self.metadata[index_value])
            distance = float(distances[0][rank])
            metadata.update(
                {
                    "score": 1.0 / (1.0 + distance),
                    "distance": distance,
                    "source": "vector",
                }
            )
            results.append(metadata)
        return results

    def save(self) -> None:
        self.storage_path.mkdir(parents=True, exist_ok=True)
        (self.storage_path / "store.pkl").write_bytes(self._metadata_bytes())
        index_bytes = self._index_bytes()
        if index_bytes is not None:
            (self.storage_path / "index.faiss").write_bytes(index_bytes)

    def load(self) -> None:
        payload_path = self.storage_path / "store.pkl"
        if not payload_path.exists():
            return
        self._load_metadata_bytes(payload_path.read_bytes())
        faiss_path = self.storage_path / "index.faiss"
        if faiss is not None and faiss_path.exists():
            self._load_index_bytes(faiss_path.read_bytes())
            return
        self._rebuild_index()

    def save_to_backend(self, storage_backend, prefix: str = "") -> None:
        storage_backend.upload_bytes(self._backend_key(prefix, "store.pkl"), self._metadata_bytes())
        index_bytes = self._index_bytes()
        if index_bytes is not None:
            storage_backend.upload_bytes(self._backend_key(prefix, "index.faiss"), index_bytes)

    def load_from_backend(self, storage_backend, prefix: str = "") -> None:
        metadata_key = self._backend_key(prefix, "store.pkl")
        if not storage_backend.exists(metadata_key):
            return
        self._load_metadata_bytes(storage_backend.download_bytes(metadata_key))
        index_key = self._backend_key(prefix, "index.faiss")
        if faiss is not None and storage_backend.exists(index_key):
            self._load_index_bytes(storage_backend.download_bytes(index_key))
            return
        self._rebuild_index()

    def _backend_key(self, prefix: str, filename: str) -> str:
        cleaned = prefix.strip("/")
        return f"{cleaned}/{filename}" if cleaned else filename

    def _metadata_bytes(self) -> bytes:
        payload = {
            "embedding_dim": self.embedding_dim,
            "metadata": self.metadata,
        }
        return pickle.dumps(payload)

    def _load_metadata_bytes(self, data: bytes) -> None:
        payload = pickle.loads(data)
        self.metadata = payload["metadata"]
        self.embedding_dim = payload["embedding_dim"]
        self._ensure_index(self.embedding_dim)

    def _index_bytes(self) -> bytes | None:
        if faiss is None or self.index is None or not hasattr(faiss, "write_index"):
            return None
        with NamedTemporaryFile(suffix=".faiss") as temp_file:
            faiss.write_index(self.index, temp_file.name)
            return Path(temp_file.name).read_bytes()

    def _load_index_bytes(self, data: bytes) -> None:
        if faiss is None:
            self._rebuild_index()
            return
        with NamedTemporaryFile(suffix=".faiss") as temp_file:
            Path(temp_file.name).write_bytes(data)
            self.index = faiss.read_index(temp_file.name)

    def _rebuild_index(self) -> None:
        if not self.metadata:
            self.index = NumpyIndex(self.embedding_dim)
            return
        vectors = np.asarray(
            self.embedder.encode([item["text"] for item in self.metadata]),
            dtype="float32",
        )
        self.embedding_dim = vectors.shape[1]
        self.index = NumpyIndex(self.embedding_dim)
        self.index.add(vectors)
