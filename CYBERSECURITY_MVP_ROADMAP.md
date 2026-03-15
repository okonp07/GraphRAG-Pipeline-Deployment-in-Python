# Cybersecurity GraphRAG MVP Roadmap

This repository will be evolved from a generic GraphRAG demo into a cybersecurity research and analyst assistant with end-to-end ingestion, retrieval, answer generation, and a usable web frontend.

## Product Goal

Build a browser-based cybersecurity assistant that can:

- ingest security reports, advisories, playbooks, and notes
- extract cybersecurity entities and relationships
- retrieve relevant evidence through vector and graph search
- answer questions with citations and supporting passages
- expose the workflow through an interactive frontend

## Current Strengths

- working Streamlit frontend
- document ingestion and chunking
- first-class dataset ingestion path for cybersecurity corpora
- vector search with local fallback
- graph indexing with Neo4j fallback mode
- hybrid retrieval service layer
- local and cloud storage support
- automated tests

## Gaps To Close

- entity extraction is still lightweight and keyword-driven
- no graph exploration UI yet
- no cybersecurity evaluation dataset or benchmark flow yet

## MVP Scope

Phase 1 should deliver a usable analyst assistant without fine-tuning.

### Ingestion

- support `.txt`, `.md`, `.json`
- add `.pdf` and `.html`
- normalize metadata such as title, source, chunk id, and document type
- extract cybersecurity entities such as CVEs, ATT&CK techniques, hashes, IPs, and domains

### Retrieval

- keep hybrid graph + vector retrieval
- add exact-match boosting for CVEs, ATT&CK IDs, hashes, IPs, and domains
- return ranked evidence with traceable source metadata

### Generation

- add a response generator module
- produce concise answers grounded only in retrieved evidence
- include citations and confidence notes

### Frontend

- chat-style interaction instead of one-shot search only
- source panel for retrieved passages
- upload/build/index workflow
- graph summary for matched entities

### Deployment

- local mode for development
- hosted mode with Neo4j AuraDB and persistent artifact storage

## Implementation Order

1. Upgrade domain extraction and retrieval quality.
2. Add answer generation with citations.
3. Expand ingestion to PDF and HTML.
4. Improve frontend UX for analyst workflows.
5. Add evaluation, deployment polish, and monitoring.
6. Revisit fine-tuning only after the retrieval app performs well.

## Immediate Next Tasks

- strengthen `src/utils.py` entity extraction
- add tests for CVE, ATT&CK, IP, hash, and domain extraction
- add a generator service module for evidence-grounded answers
- wire the generator into `src/app_service.py` and `app.py`
- update the UI copy and branding to be cybersecurity-specific
