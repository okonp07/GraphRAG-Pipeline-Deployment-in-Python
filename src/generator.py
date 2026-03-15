"""Grounded answer generation for the cybersecurity assistant."""

from __future__ import annotations

import re
from typing import Any, Dict, List


def _split_sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [part.strip() for part in parts if part.strip()]


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z0-9_.:-]+", text.lower()))


class AnswerGenerator:
    """Builds concise answers from retrieved evidence."""

    def generate(self, query_text: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not results:
            return {
                "answer": "I could not find enough evidence in the indexed documents to answer that question yet.",
                "citations": [],
                "confidence": "low",
                "answer_mode": "fallback",
            }

        top_results = results[:3]
        query_tokens = _tokenize(query_text)
        evidence_items = []
        seen_sentences = set()

        for result in top_results:
            sentences = _split_sentences(result.get("text", ""))
            best_sentence = result.get("text", "").strip()
            best_score = -1
            for sentence in sentences:
                sentence_tokens = _tokenize(sentence)
                overlap = len(query_tokens & sentence_tokens)
                score = overlap
                if result.get("matched_entities"):
                    score += len(result["matched_entities"])
                if score > best_score:
                    best_sentence = sentence
                    best_score = score
            normalized = best_sentence.lower()
            if normalized in seen_sentences:
                continue
            seen_sentences.add(normalized)
            evidence_items.append(
                {
                    "document_id": result.get("id", ""),
                    "source_path": result.get("source_path", "unknown"),
                    "text": best_sentence,
                    "combined_score": float(result.get("combined_score", 0.0)),
                    "matched_entities": result.get("matched_entities", []),
                }
            )

        answer_lines = []
        lead = evidence_items[0]["text"]
        answer_lines.append(f"Based on the indexed evidence, {lead}")
        if len(evidence_items) > 1:
            supporting = " ".join(item["text"] for item in evidence_items[1:3])
            answer_lines.append(f"Supporting evidence also indicates: {supporting}")

        confidence = "high" if evidence_items[0]["combined_score"] >= 1.0 else "medium"
        if len(evidence_items) == 1 and confidence == "medium":
            confidence = "low"

        return {
            "answer": " ".join(answer_lines).strip(),
            "citations": evidence_items,
            "confidence": confidence,
            "answer_mode": "fallback",
        }
