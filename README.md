# GraphRAG Pipeline with Neo4j and Vector DB

A retrieval-augmented generation (RAG) system that combines a knowledge graph (Neo4j) with vector similarity search to improve document retrieval for question answering workloads.

## Overview

This repository now includes a complete Python project structure alongside the original notebooks. The runnable code implements a hybrid retrieval pipeline that uses:

- **Neo4j** for graph-based document/entity lookup
- **FAISS** for semantic vector search
- **A hybrid retriever** to combine graph and vector results into one ranked output
- **Streamlit** for a browser-based interface
- **S3-compatible object storage** for persistent online artifacts

The current implementation is designed to work in two modes:

- **Full mode:** Neo4j + FAISS + sentence-transformers
- **Cloud mode:** Streamlit Cloud + Neo4j AuraDB + S3-compatible storage
- **Local fallback mode:** in-memory graph search + deterministic hashing embeddings when optional services or models are unavailable

That means you can develop and test the project locally even before connecting a live Neo4j instance.

## Features

- Document ingestion and processing pipeline
- Text chunking and embedding generation
- Knowledge graph construction from extracted cybersecurity terms
- Vector similarity search for semantic queries
- Graph traversal for relationship-based retrieval
- Hybrid retrieval combining graph and vector results
- Simple query interface through Python scripts
- Streamlit frontend for non-technical users
- Streamlit Cloud deployment configuration
- Streamlit secrets-based configuration support
- S3-compatible artifact persistence for hosted deployments
- Example scripts and automated tests

## Installation

### Prerequisites

- Python 3.8+
- Neo4j Database (optional for local development, required for live graph storage)
- Git

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/okonp07/GraphRAG-Pipeline-Deployment-in-Python.git
   cd GraphRAG-Pipeline-Deployment-in-Python
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Configure your environment:
   ```bash
   cp .env.example .env
   ```

4. Update `.env` with your Neo4j connection details if you want live Neo4j support. Set `GRAPHRAG_USE_NEO4J=true` to enable it.

### Streamlit Cloud Deployment

To deploy online:

1. Push this repository to GitHub.
2. Create a Streamlit Community Cloud app that points at `app.py`.
3. Add your production secrets in the Streamlit Cloud secrets editor using the template in [.streamlit/secrets.toml.example](/Users/researchanddevelopment2/Documents/Zindi/GraphRAG-Pipeline-Deployment-in-Python/.streamlit/secrets.toml.example).
4. Use:
   - a managed Neo4j instance such as Neo4j AuraDB
   - an S3-compatible bucket for persistent vector and document artifacts

The repo includes Streamlit config in [.streamlit/config.toml](/Users/researchanddevelopment2/Documents/Zindi/GraphRAG-Pipeline-Deployment-in-Python/.streamlit/config.toml).

## Usage

### Frontend App

Launch the Streamlit app for a browser-based experience:

```bash
streamlit run app.py
```

The app lets users:

- upload documents
- build the knowledge base
- load bundled sample files
- ask questions in plain English
- view the best match and supporting results without using the command line

For hosted deployments, configure `storage.backend = "s3"` in Streamlit secrets so uploaded knowledge bases persist outside the app container.

### Data Ingestion

Process documents and build both vector embeddings and the knowledge graph:

```bash
python ingest.py --data-dir /path/to/your/documents
```

Supported input formats:

- `.txt`
- `.md`
- `.markdown`
- `.json`

### Querying the System

Run queries against the combined GraphRAG system:

```bash
python query.py --query "Your natural language query here"
```

### Advanced Usage

Adjust retrieval weights and result counts:

```bash
python query.py --query "How do I reduce phishing risk?" --graph-weight 0.7 --vector-weight 0.3 --top-k 5
```

## Architecture

The system consists of four main components:

1. **Document Processor:** Parses files, normalizes text, chunks documents, and extracts basic cybersecurity entities.
2. **Vector Store:** Creates embeddings and stores them in FAISS, with a NumPy fallback when FAISS is unavailable.
3. **Knowledge Graph:** Stores document/entity relationships in Neo4j, with an in-memory fallback for local development and tests.
4. **Hybrid Retriever:** Combines graph and vector search results using configurable weights.

## Example Query Flow

1. User submits a question.
2. The query is embedded for vector search.
3. The query is scanned for cybersecurity entities for graph search.
4. Retrieval runs against:
   - Neo4j or the in-memory graph index
   - FAISS or the fallback vector index
5. Results are merged, weighted, ranked, and returned.

## File Structure

```text
├── README.md
├── LICENSE
├── requirements.txt
├── .env.example
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.example
├── config.py
├── app.py
├── ingest.py
├── query.py
├── src/
│   ├── __init__.py
│   ├── app_service.py
│   ├── ingest.py
│   ├── query.py
│   ├── storage.py
│   ├── vector_store.py
│   ├── knowledge_graph.py
│   ├── hybrid_retriever.py
│   └── utils.py
├── examples/
│   ├── sample_query.py
│   ├── batch_process.py
│   └── data/
│       ├── phishing.txt
│       └── ransomware.txt
├── tests/
│   ├── test_vector_store.py
│   ├── test_knowledge_graph.py
│   └── test_retrieval.py
├── Knowledge_Base_&_GraphRAG.ipynb
└── Bonus_Project _Deploying_a_Simple_RAG_Pipeline_in_python.ipynb
```

## Configuration

Edit [config.py](config.py) or update environment variables in `.env` to customize:

- Chunk size and overlap for text splitting
- Embedding model selection
- Fallback embedding dimension
- Neo4j connection parameters
- Storage backend, bucket, prefix, and region
- Retrieval weights and default `top_k`
- Artifact output paths

When running on Streamlit Cloud, configuration can come from:

- environment variables
- `.env` for local development
- Streamlit secrets for hosted deployment

## Examples

Run the packaged examples after ingestion:

```bash
python examples/sample_query.py
python examples/batch_process.py
```

## Testing

Run the automated test suite with:

```bash
pytest
```

To smoke test the frontend locally:

```bash
streamlit run app.py
```

## Online Persistence

The app now supports persistent online storage for uploaded knowledge bases.

- `local` storage backend:
  stores FAISS indexes and document metadata on the local filesystem
- `s3` storage backend:
  stores FAISS indexes and document metadata in an S3-compatible bucket

Artifacts persisted online include:

- vector index metadata
- FAISS index binary when available
- document metadata JSON

This avoids losing uploaded knowledge bases when the hosted app restarts.

## Contributing

Contributions are welcome. A typical workflow is:

1. Fork the repository.
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m "Add some amazing feature"`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgements

- [Neo4j](https://neo4j.com/) for graph database technology
- [FAISS](https://github.com/facebookresearch/faiss) for vector similarity search
- [Sentence Transformers](https://www.sbert.net/) for embedding workflows
- [LangChain](https://github.com/langchain-ai/langchain) for broader RAG inspiration

## Author

**Okon Prince**  
*Data Scientist and AI Researcher*  
Developer, Python GraphRAG Pipeline  
Specialized in AI applications for cybersecurity, environmental intelligence, and education.
