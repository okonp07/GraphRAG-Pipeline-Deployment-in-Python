"""Streamlit frontend for the GraphRAG pipeline."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import streamlit as st

from config import get_settings
from src.app_service import GraphRAGService


st.set_page_config(
    page_title="GraphRAG Assistant",
    page_icon="docs",
    layout="wide",
)


def _init_service() -> GraphRAGService:
    settings = get_settings()
    return GraphRAGService.from_settings(settings)


def _format_source_label(path_value: str) -> str:
    path = Path(path_value)
    return path.name or str(path)


def main() -> None:
    st.title("GraphRAG Assistant")
    st.caption("A simple document search experience for non-technical users.")

    if "service" not in st.session_state:
        st.session_state.service = _init_service()
    service: GraphRAGService = st.session_state.service

    with st.sidebar:
        st.header("Workspace")
        st.write("Upload documents, build the knowledge base, and then ask questions in plain English.")

        graph_weight = st.slider("Graph weight", 0.0, 1.0, float(service.settings.graph_weight), 0.1)
        vector_weight = st.slider("Vector weight", 0.0, 1.0, float(service.settings.vector_weight), 0.1)
        top_k = st.slider("Results to show", 1, 10, int(service.settings.top_k), 1)
        service.configure_weights(graph_weight=graph_weight, vector_weight=vector_weight)

        st.subheader("Upload documents")
        uploaded_files = st.file_uploader(
            "Supported formats: TXT, MD, Markdown, JSON",
            type=["txt", "md", "markdown", "json"],
            accept_multiple_files=True,
        )

        if st.button("Build knowledge base", use_container_width=True):
            if not uploaded_files:
                st.warning("Upload at least one document before building the knowledge base.")
            else:
                with TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    for uploaded_file in uploaded_files:
                        destination = temp_path / uploaded_file.name
                        destination.write_bytes(uploaded_file.getbuffer())
                    with st.spinner("Processing documents and building the retrieval index..."):
                        count = service.ingest_directory(temp_path)
                st.success(f"Knowledge base updated with {count} document chunk(s).")

        if st.button("Load sample data", use_container_width=True):
            sample_dir = Path("examples/data")
            with st.spinner("Loading the bundled sample documents..."):
                count = service.ingest_directory(sample_dir)
            st.success(f"Loaded {count} sample document chunk(s).")

        if st.button("Clear session data", use_container_width=True):
            service.reset()
            st.success("Cleared the in-app knowledge base.")

        st.divider()
        st.metric("Indexed chunks", service.document_count)
        st.metric("Neo4j enabled", "Yes" if service.settings.use_neo4j else "No")
        st.metric("Storage backend", service.settings.storage_backend.upper())

    st.subheader("Ask a question")
    query = st.text_input(
        "Type a question about the uploaded documents",
        placeholder="For example: How can we reduce phishing risk?",
    )

    if st.button("Search", type="primary", use_container_width=True):
        if not query.strip():
            st.warning("Enter a question to search the knowledge base.")
        elif service.document_count == 0:
            st.warning("Build the knowledge base first by uploading files or loading the sample data.")
        else:
            with st.spinner("Searching the knowledge base..."):
                results = service.query(query, top_k=top_k)

            if not results:
                st.info("No relevant results were found for that question.")
            else:
                top_result = results[0]
                st.success("Search complete.")
                st.markdown("### Best Match")
                st.write(top_result["text"])
                if top_result.get("matched_entities"):
                    st.caption("Matched topics: " + ", ".join(top_result["matched_entities"]))

                st.markdown("### Supporting Results")
                for index, result in enumerate(results, start=1):
                    title = f"{index}. {_format_source_label(result.get('source_path', 'Unknown source'))}"
                    with st.expander(title, expanded=index == 1):
                        st.write(result["text"])
                        left, right = st.columns(2)
                        left.metric("Combined score", f"{result['combined_score']:.3f}")
                        right.write("Sources: " + ", ".join(result.get("retrieval_sources", [])))
                        if result.get("matched_entities"):
                            st.write("Matched entities: " + ", ".join(result["matched_entities"]))
                        if result.get("source_path"):
                            st.caption(f"Source file: {result['source_path']}")


if __name__ == "__main__":
    main()
