"""Knowledge graph operations with Neo4j support and an in-memory fallback."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Iterable, List

try:
    from neo4j import GraphDatabase  # type: ignore
except ImportError:  # pragma: no cover
    GraphDatabase = None

from .utils import extract_entities


class KnowledgeGraph:
    """Stores extracted entities and supports graph-based retrieval."""

    def __init__(
        self,
        uri: str = "",
        username: str = "neo4j",
        password: str = "",
        database: str = "neo4j",
        enabled: bool = False,
    ):
        self.uri = uri
        self.username = username
        self.password = password
        self.database = database
        self.enabled = enabled and bool(uri) and GraphDatabase is not None
        self.driver = None
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.entity_to_docs: Dict[str, set[str]] = defaultdict(set)
        self.entity_types: Dict[str, str] = {}
        self.relationships: List[Dict[str, str]] = []
        if self.enabled:
            self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self) -> None:
        if self.driver is not None:
            self.driver.close()

    def clear(self) -> None:
        self.documents.clear()
        self.entity_to_docs.clear()
        self.entity_types.clear()
        self.relationships.clear()
        if self.driver is None:
            return
        with self.driver.session(database=self.database) as session:
            session.run("MATCH (n) DETACH DELETE n")
            session.run(
                "CREATE CONSTRAINT document_id IF NOT EXISTS "
                "FOR (d:Document) REQUIRE d.id IS UNIQUE"
            )
            session.run(
                "CREATE CONSTRAINT entity_name IF NOT EXISTS "
                "FOR (e:Entity) REQUIRE e.name IS UNIQUE"
            )

    def ingest_documents(self, documents: Iterable[Dict[str, Any]]) -> None:
        for doc in documents:
            doc_id = str(doc["id"])
            entities = doc.get("entities") or extract_entities(doc["text"])
            payload = dict(doc)
            payload["entities"] = entities
            self.documents[doc_id] = payload
            for entity in entities:
                name = entity["name"].lower()
                entity_type = entity["type"]
                self.entity_to_docs[name].add(doc_id)
                self.entity_types[name] = entity_type
            self._build_relationships(entities)
        if self.driver is not None:
            self._sync_to_neo4j()

    def _build_relationships(self, entities: List[Dict[str, str]]) -> None:
        for left_index, left in enumerate(entities):
            for right in entities[left_index + 1 :]:
                if left["name"] == right["name"]:
                    continue
                relation_type = "RELATED_TO"
                if left["type"] == "THREAT" and right["type"] == "VULNERABILITY":
                    relation_type = "EXPLOITS"
                elif left["type"].startswith("DEFENSE") and right["type"] == "THREAT":
                    relation_type = "MITIGATES"
                self.relationships.append(
                    {
                        "source": left["name"].lower(),
                        "target": right["name"].lower(),
                        "type": relation_type,
                    }
                )

    def _sync_to_neo4j(self) -> None:
        assert self.driver is not None
        with self.driver.session(database=self.database) as session:
            for doc in self.documents.values():
                session.run(
                    "MERGE (d:Document {id: $id}) "
                    "SET d.text = $text, d.source_path = $source_path, d.chunk_index = $chunk_index",
                    id=str(doc["id"]),
                    text=doc["text"],
                    source_path=doc.get("source_path", ""),
                    chunk_index=doc.get("chunk_index", 0),
                )
                for entity in doc["entities"]:
                    session.run(
                        "MERGE (e:Entity {name: $name}) "
                        "SET e.type = $type",
                        name=entity["name"].lower(),
                        type=entity["type"],
                    )
                    session.run(
                        "MATCH (d:Document {id: $doc_id}) "
                        "MATCH (e:Entity {name: $entity_name}) "
                        "MERGE (d)-[:MENTIONS]->(e)",
                        doc_id=str(doc["id"]),
                        entity_name=entity["name"].lower(),
                    )
            seen = set()
            for relationship in self.relationships:
                dedupe_key = (
                    relationship["source"],
                    relationship["target"],
                    relationship["type"],
                )
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)
                session.run(
                    "MATCH (a:Entity {name: $source}) "
                    "MATCH (b:Entity {name: $target}) "
                    f"MERGE (a)-[:{relationship['type']}]->(b)",
                    source=relationship["source"],
                    target=relationship["target"],
                )

    def search(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        entities = extract_entities(query_text)
        if not entities:
            return []
        if self.driver is not None:
            return self._search_neo4j(entities, top_k)
        return self._search_in_memory(entities, top_k)

    def _search_in_memory(self, entities: List[Dict[str, str]], top_k: int) -> List[Dict[str, Any]]:
        scores: Dict[str, float] = defaultdict(float)
        matched_entities: Dict[str, List[str]] = defaultdict(list)
        for entity in entities:
            name = entity["name"].lower()
            for doc_id in self.entity_to_docs.get(name, set()):
                scores[doc_id] += 1.0
                matched_entities[doc_id].append(name)
        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:top_k]
        results = []
        for doc_id, score in ranked:
            document = dict(self.documents[doc_id])
            document.update(
                {
                    "score": float(score),
                    "matched_entities": matched_entities[doc_id],
                    "source": "graph",
                }
            )
            results.append(document)
        return results

    def _search_neo4j(self, entities: List[Dict[str, str]], top_k: int) -> List[Dict[str, Any]]:
        assert self.driver is not None
        names = [entity["name"].lower() for entity in entities]
        query = (
            "MATCH (d:Document)-[:MENTIONS]->(e:Entity) "
            "WHERE e.name IN $names "
            "RETURN d.id AS document_id, d.text AS text, d.source_path AS source_path, "
            "d.chunk_index AS chunk_index, collect(e.name) AS matched_entities, "
            "count(e) AS relevance "
            "ORDER BY relevance DESC LIMIT $top_k"
        )
        results = []
        with self.driver.session(database=self.database) as session:
            for record in session.run(query, names=names, top_k=top_k):
                results.append(
                    {
                        "id": record["document_id"],
                        "text": record["text"],
                        "source_path": record["source_path"],
                        "chunk_index": record["chunk_index"],
                        "matched_entities": record["matched_entities"],
                        "score": float(record["relevance"]),
                        "source": "graph",
                    }
                )
        return results
