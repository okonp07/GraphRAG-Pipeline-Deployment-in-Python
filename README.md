# Cybersecurity GraphRAG Assistant

A cybersecurity-focused GraphRAG project that combines document ingestion, vector retrieval, entity-aware graph search, and an interactive web app.

This repository is now the canonical home for the project. The older notebook-only cybersecurity prototype is being folded into this codebase so we can build one clean end-to-end product instead of maintaining two overlapping repos.

## What This Project Does

The assistant is designed to help users work with cybersecurity knowledge sources such as advisories, incident notes, malware writeups, and security playbooks.

It currently supports:

- document ingestion and chunking
- parsing of TXT, Markdown, JSON, HTML, and PDF documents
- ingestion from a cybersecurity dataset source such as `zeroshot/cybersecurity-corpus`
- vector similarity search
- graph-based retrieval over extracted cybersecurity entities
- hybrid ranking across graph and vector search
- a Streamlit frontend for document upload and search
- local fallback mode for development without full cloud infrastructure

## Why This Repo Is The Main One

Compared with the older notebook prototype, this repository already has:

- a proper Python project structure
- a reusable service layer
- automated tests
- a browser-based frontend
- local and cloud storage support
- room to add answer generation, richer ingestion, and deployment polish

The notebook prototype is being retained here only as legacy reference material while the production-ready app evolves in this repo.

## Current Architecture

The project currently consists of four core layers:

1. `Ingestion`: reads supported documents, normalizes text, chunks content, and extracts cybersecurity entities.
2. `Vector Retrieval`: embeds chunks and searches them semantically using FAISS or a NumPy fallback.
3. `Knowledge Graph`: stores document-to-entity relationships in Neo4j or an in-memory fallback.
4. `Frontend + Service Layer`: exposes ingestion and retrieval through Streamlit and shared Python services.

## Cybersecurity Direction

This codebase is being specialized into a cybersecurity assistant that can reason over:

- threats such as ransomware, phishing, spyware, and breaches
- defensive concepts such as MFA, patching, EDR, and zero trust
- structured indicators such as CVEs, ATT&CK technique IDs, IP addresses, hashes, and domains

The first implementation pass already upgraded entity extraction to recognize several of those structured indicators.

## MVP Roadmap

The near-term goal is a full cybersecurity GraphRAG assistant with cited answers.

Planned milestones:

1. strengthen cybersecurity extraction and retrieval quality
2. add grounded answer generation with citations
3. support richer ingestion formats such as PDF and HTML
4. improve the frontend into a chat-style analyst experience
5. polish deployment, persistence, and evaluation

The detailed working plan lives in [CYBERSECURITY_MVP_ROADMAP.md](/Users/researchanddevelopment2/Documents/Zindi/GraphRAG-Pipeline-Deployment-in-Python/CYBERSECURITY_MVP_ROADMAP.md).

## Project Structure

```text
├── app.py
├── config.py
├── ingest.py
├── query.py
├── CYBERSECURITY_MVP_ROADMAP.md
├── notebooks/
│   └── legacy/
├── src/
│   ├── app_service.py
│   ├── hybrid_retriever.py
│   ├── ingest.py
│   ├── knowledge_graph.py
│   ├── query.py
│   ├── storage.py
│   ├── utils.py
│   └── vector_store.py
├── examples/
├── tests/
└── .streamlit/
```

## Installation

### Prerequisites

- Python 3.8+
- Git
- Neo4j if you want live graph storage instead of fallback mode

### Setup

```bash
git clone https://github.com/okonp07/GraphRAG-Pipeline-Deployment-in-Python.git
cd GraphRAG-Pipeline-Deployment-in-Python
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

If you use local environment variables, create a `.env` file and add your Neo4j and storage settings as needed.

## Running The App

Start the frontend:

```bash
streamlit run app.py
```

The app lets you:

- upload security-related documents
- load a built-in cybersecurity corpus
- build a knowledge base
- load bundled sample data
- ask questions in plain English
- inspect supporting evidence returned by the retriever

## Ingestion And Querying

Ingest a directory of documents:

```bash
python ingest.py --data-dir /path/to/your/documents
```

Ingest the default cybersecurity dataset source:

```bash
python ingest.py --dataset-name zeroshot/cybersecurity-corpus --dataset-split train
```

You can also configure the default dataset source through:

- `GRAPHRAG_DATASET_NAME`
- `GRAPHRAG_DATASET_SPLIT`
- `GRAPHRAG_DATASET_TEXT_FIELD`

Run a query from the command line:

```bash
python query.py --query "How do we reduce phishing risk?"
```

## Supported Formats Today

- `.txt`
- `.md`
- `.markdown`
- `.json`
- `.html`
- `.htm`
- `.pdf`

## Testing

Run the test suite with:

```bash
pytest
```

## Legacy Assets

Legacy notebooks are being retained in `notebooks/legacy/` as reference material during the merge. They are not the primary implementation path anymore.
