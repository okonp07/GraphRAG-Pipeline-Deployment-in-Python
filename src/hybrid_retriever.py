"""Hybrid retrieval that combines graph and vector search results."""

from __future__ import annotations

from typing import Any, Dict, List


class HybridRetriever:
    def __init__(self, vector_store, knowledge_graph, vector_weight: float = 0.5, graph_weight: float = 0.5):
        self.vector_store = vector_store
        self.knowledge_graph = knowledge_graph
        self.vector_weight = vector_weight
        self.graph_weight = graph_weight

    def search(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        vector_results = self.vector_store.search(query_text, top_k=top_k)
        graph_results = self.knowledge_graph.search(query_text, top_k=top_k)

        combined: Dict[str, Dict[str, Any]] = {}

        for result in vector_results:
            doc_id = str(result["id"])
            payload = dict(result)
            payload["vector_score"] = result["score"]
            payload["graph_score"] = 0.0
            payload["combined_score"] = self.vector_weight * result["score"]
            payload["retrieval_sources"] = ["vector"]
            combined[doc_id] = payload

        for result in graph_results:
            doc_id = str(result["id"])
            graph_score = float(result["score"])
            if doc_id not in combined:
                payload = dict(result)
                payload["vector_score"] = 0.0
                payload["graph_score"] = graph_score
                payload["combined_score"] = self.graph_weight * graph_score
                payload["retrieval_sources"] = ["graph"]
                combined[doc_id] = payload
                continue
            combined[doc_id]["graph_score"] = graph_score
            combined[doc_id]["combined_score"] += self.graph_weight * graph_score
            if "graph" not in combined[doc_id]["retrieval_sources"]:
                combined[doc_id]["retrieval_sources"].append("graph")
            if result.get("matched_entities"):
                combined[doc_id]["matched_entities"] = result["matched_entities"]

        ranked = sorted(
            combined.values(),
            key=lambda item: item["combined_score"],
            reverse=True,
        )
        return ranked[:top_k]
