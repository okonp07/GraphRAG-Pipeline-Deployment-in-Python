# Cybersecurity GraphRAG Assistant

A cybersecurity question-answering system that combines document ingestion, hybrid retrieval, entity-aware graph search, and a browser-based analyst interface.

## Live App

## [Open the Streamlit App](https://graphrag-pipeline-deployment-in-python-uxc9cluat75f24nn8vzcca.streamlit.app)

This repository is the main home of the project. It unifies the earlier notebook prototype and the application code into one working end-to-end solution.

## What This Solution Does

This project helps a user build a cybersecurity knowledge assistant from two kinds of sources:

- their own uploaded security material such as reports, notes, advisories, playbooks, and web content
- a built-in cybersecurity corpus such as `zeroshot/cybersecurity-corpus`

Once content is indexed, the application lets the user ask cybersecurity questions in plain English and returns:

- a synthesized answer grounded in retrieved evidence
- supporting citations
- ranked results from hybrid retrieval
- matched cybersecurity entities extracted from the documents

The goal is to make cybersecurity knowledge easier to search, connect, and explain, especially when the source material is spread across many files or reports.

## Why This Project Exists

Traditional document search is often not enough for cybersecurity work. Security questions frequently involve:

- exact indicators such as CVEs, ATT&CK technique IDs, hashes, IP addresses, and domains
- conceptual relationships such as which controls mitigate a threat
- mixed evidence across writeups, alerts, and internal notes

This project addresses that by combining semantic search with graph-aware retrieval so the assistant can use both:

- vector similarity for meaning and context
- entity and relationship signals for structured cyber reasoning

## Core Capabilities

- ingest local documents from `.txt`, `.md`, `.markdown`, `.json`, `.html`, `.htm`, and `.pdf`
- ingest a built-in cybersecurity dataset from Hugging Face
- normalize and chunk raw text for retrieval
- extract cybersecurity entities such as threats, defensive concepts, CVEs, ATT&CK techniques, hashes, domains, and IP addresses
- build a vector index for semantic search
- build a document-entity graph for graph-based lookup
- combine graph and vector evidence in a hybrid retriever
- generate grounded answers with citations
- expose the workflow through a multipage Streamlit user interface

## How The Solution Works

The application follows a four-stage flow.

### 1. Ingestion

Documents or dataset records are loaded and normalized into plain text. Large texts are split into chunks so retrieval can work at a more useful evidence level instead of over entire long files.

### 2. Cybersecurity Enrichment

Each chunk is scanned for cybersecurity entities and structured indicators such as:

- `CVE-2024-12345`
- `T1059`
- IP addresses
- domains
- hashes
- common cyber terms such as phishing, ransomware, MFA, zero trust, EDR, and patching

These entities become part of the graph-aware retrieval path.

### 3. Hybrid Retrieval

The system searches the knowledge base in two ways:

- vector retrieval to find semantically similar chunks
- graph retrieval to find chunks connected to extracted cybersecurity entities

The results are merged into one ranked list using configurable graph and vector weights.

### 4. Grounded Answering

The assistant synthesizes a response from the top retrieved evidence and returns:

- the answer
- a confidence label
- citations
- supporting retrieved passages

## User Experience

The Streamlit app is now organized as a multipage workspace so the interface is less crowded and each task has its own place.

### Ask Assistant

This page is focused on question answering. It is where the user:

- asks cybersecurity questions
- receives grounded answers
- reviews citations
- inspects supporting retrieval results

### Knowledge Base

This page is focused on data management. It is where the user:

- uploads local documents
- loads the bundled sample collection
- imports the built-in cybersecurity corpus
- clears the current workspace

### Retrieval Settings

This page is focused on tuning and diagnostics. It is where the user:

- adjusts graph and vector weights
- changes result depth
- reviews runtime retrieval settings
- inspects the current workspace configuration

Across those pages, the app supports two main ways to build the knowledge base:

### Bring your own material

Users can upload their own security documents and build a custom knowledge base from them.

### Use the built-in corpus

Users can also load a cybersecurity dataset directly inside the app, which gives the product an inbuilt knowledge source even before any local files are uploaded.

That means the app already supports the two modes you wanted:

- uploaded knowledge
- somewhat inbuilt knowledge

## Current Architecture

The solution is organized around these main layers:

1. `Ingestion`
   Loads documents and datasets, normalizes them, and creates retrieval-ready chunks.
2. `Cybersecurity Extraction`
   Identifies relevant entities and indicators in each chunk.
3. `Vector Retrieval`
   Uses FAISS, or a fallback NumPy index, to run semantic search.
4. `Knowledge Graph`
   Uses Neo4j, or an in-memory fallback, to store document-entity relationships.
5. `Hybrid Retrieval`
   Combines graph and vector evidence into one ranked result set.
6. `Answer Generation`
   Produces grounded answers and citations from the top evidence.
7. `Frontend`
   Exposes the full workflow through a multipage Streamlit workspace.

## Key Files

- [app.py](/Users/researchanddevelopment2/Documents/Zindi/GraphRAG-Pipeline-Deployment-in-Python/app.py)
  Multipage landing page for the app.
- [pages/1_Ask_Assistant.py](/Users/researchanddevelopment2/Documents/Zindi/GraphRAG-Pipeline-Deployment-in-Python/pages/1_Ask_Assistant.py)
  Dedicated question-answering page for grounded responses and citations.
- [pages/2_Knowledge_Base.py](/Users/researchanddevelopment2/Documents/Zindi/GraphRAG-Pipeline-Deployment-in-Python/pages/2_Knowledge_Base.py)
  Knowledge-base management page for uploads, sample data, and the built-in corpus.
- [pages/3_Retrieval_Settings.py](/Users/researchanddevelopment2/Documents/Zindi/GraphRAG-Pipeline-Deployment-in-Python/pages/3_Retrieval_Settings.py)
  Retrieval tuning page for graph/vector weights and result depth.
- [src/frontend.py](/Users/researchanddevelopment2/Documents/Zindi/GraphRAG-Pipeline-Deployment-in-Python/src/frontend.py)
  Shared Streamlit styling, service/session state, and reusable UI helpers.
- [src/app_service.py](/Users/researchanddevelopment2/Documents/Zindi/GraphRAG-Pipeline-Deployment-in-Python/src/app_service.py)
  Main orchestration layer for ingestion, retrieval, and answer generation.
- [src/dataset_loader.py](/Users/researchanddevelopment2/Documents/Zindi/GraphRAG-Pipeline-Deployment-in-Python/src/dataset_loader.py)
  Loader for dataset-backed cybersecurity corpora.
- [src/generator.py](/Users/researchanddevelopment2/Documents/Zindi/GraphRAG-Pipeline-Deployment-in-Python/src/generator.py)
  Grounded answer synthesis.
- [src/knowledge_graph.py](/Users/researchanddevelopment2/Documents/Zindi/GraphRAG-Pipeline-Deployment-in-Python/src/knowledge_graph.py)
  Graph storage and graph search.
- [src/vector_store.py](/Users/researchanddevelopment2/Documents/Zindi/GraphRAG-Pipeline-Deployment-in-Python/src/vector_store.py)
  Vector indexing and semantic search.
- [src/utils.py](/Users/researchanddevelopment2/Documents/Zindi/GraphRAG-Pipeline-Deployment-in-Python/src/utils.py)
  Parsing, chunking, and cybersecurity entity extraction helpers.

## Project Structure

```text
├── app.py
├── pages/
│   ├── 1_Ask_Assistant.py
│   ├── 2_Knowledge_Base.py
│   └── 3_Retrieval_Settings.py
├── config.py
├── ingest.py
├── query.py
├── CYBERSECURITY_MVP_ROADMAP.md
├── notebooks/
│   └── legacy/
├── src/
│   ├── app_service.py
│   ├── dataset_loader.py
│   ├── frontend.py
│   ├── generator.py
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

If you use local environment variables, create a `.env` file and add any Neo4j or storage settings you need.

## Running The App

Start the frontend locally:

```bash
streamlit run app.py
```

After the app opens, use Streamlit's page navigation in the sidebar to move between:

- `Ask Assistant`
- `Knowledge Base`
- `Retrieval Settings`

Or use the hosted version:

## [Launch the Streamlit App](https://graphrag-pipeline-deployment-in-python-uxc9cluat75f24nn8vzcca.streamlit.app)

## Ingestion Workflows

### Ingest local files

```bash
python ingest.py --data-dir /path/to/your/documents
```

### Ingest the built-in cybersecurity dataset

```bash
python ingest.py --dataset-name zeroshot/cybersecurity-corpus --dataset-split train
```

Optional dataset-related environment variables:

- `GRAPHRAG_DATASET_NAME`
- `GRAPHRAG_DATASET_SPLIT`
- `GRAPHRAG_DATASET_TEXT_FIELD`

## Querying

Run a query from the command line:

```bash
python query.py --query "How do we reduce phishing risk?"
```

## Supported Formats

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

## Roadmap

The working implementation plan lives in [CYBERSECURITY_MVP_ROADMAP.md](/Users/researchanddevelopment2/Documents/Zindi/GraphRAG-Pipeline-Deployment-in-Python/CYBERSECURITY_MVP_ROADMAP.md).

## Legacy Assets

The original notebook-based prototype has been preserved under [notebooks/legacy](/Users/researchanddevelopment2/Documents/Zindi/GraphRAG-Pipeline-Deployment-in-Python/notebooks/legacy) for reference, but the active implementation now lives in the application code in this repository.
