"""Streamlit frontend for the cybersecurity GraphRAG assistant."""

from __future__ import annotations

import html
from pathlib import Path
from tempfile import TemporaryDirectory

import streamlit as st

from config import get_settings
from src.app_service import GraphRAGService


st.set_page_config(
    page_title="Cybersecurity GraphRAG Assistant",
    page_icon="docs",
    layout="wide",
)


APP_CSS = """
<style>
:root {
    --bg: #f4efe4;
    --panel: rgba(255, 251, 245, 0.88);
    --panel-strong: #fffaf1;
    --ink: #182028;
    --muted: #5d6773;
    --accent: #c35b2c;
    --accent-soft: rgba(195, 91, 44, 0.12);
    --accent-deep: #7d3316;
    --line: rgba(24, 32, 40, 0.1);
    --teal: #1d6f78;
    --gold: #c89b3c;
    --shadow: 0 18px 48px rgba(61, 45, 23, 0.12);
}

.stApp {
    background:
        radial-gradient(circle at top right, rgba(29, 111, 120, 0.18), transparent 28%),
        radial-gradient(circle at top left, rgba(200, 155, 60, 0.16), transparent 24%),
        linear-gradient(180deg, #fbf7ef 0%, var(--bg) 100%);
    color: var(--ink);
}

[data-testid="stSidebar"] {
    background:
        linear-gradient(180deg, rgba(255, 248, 236, 0.96), rgba(244, 237, 224, 0.98));
    border-right: 1px solid rgba(125, 51, 22, 0.08);
}

[data-testid="stHeader"] {
    background: rgba(244, 239, 228, 0.7);
}

h1, h2, h3 {
    font-family: "Avenir Next", "Segoe UI", sans-serif;
    letter-spacing: -0.03em;
    color: var(--ink);
}

p, li, label, [data-testid="stMarkdownContainer"] {
    color: var(--ink);
}

.hero-shell {
    padding: 1.4rem 1.6rem;
    border: 1px solid rgba(29, 111, 120, 0.14);
    border-radius: 28px;
    background:
        linear-gradient(135deg, rgba(255, 248, 237, 0.95), rgba(250, 239, 221, 0.88)),
        linear-gradient(120deg, rgba(29, 111, 120, 0.08), rgba(195, 91, 44, 0.04));
    box-shadow: var(--shadow);
    position: relative;
    overflow: hidden;
}

.hero-shell::after {
    content: "";
    position: absolute;
    inset: auto -4rem -4rem auto;
    width: 14rem;
    height: 14rem;
    border-radius: 999px;
    background: radial-gradient(circle, rgba(29, 111, 120, 0.18), transparent 65%);
}

.eyebrow {
    display: inline-block;
    padding: 0.3rem 0.7rem;
    border-radius: 999px;
    background: rgba(29, 111, 120, 0.12);
    color: var(--teal);
    font-size: 0.76rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
}

.hero-title {
    margin: 0.9rem 0 0.5rem 0;
    font-size: 3rem;
    line-height: 0.95;
    max-width: 12ch;
}

.hero-copy {
    max-width: 62ch;
    color: var(--muted);
    font-size: 1rem;
}

.mini-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.75rem;
    margin-top: 1.1rem;
}

.mini-card {
    padding: 0.95rem 1rem;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.64);
    border: 1px solid rgba(24, 32, 40, 0.08);
    backdrop-filter: blur(6px);
}

.mini-label {
    color: var(--muted);
    font-size: 0.76rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.mini-value {
    margin-top: 0.35rem;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--ink);
}

.section-card {
    padding: 1.15rem 1.15rem 1rem;
    border-radius: 24px;
    background: var(--panel);
    border: 1px solid var(--line);
    box-shadow: 0 12px 30px rgba(61, 45, 23, 0.08);
}

.section-title {
    margin: 0 0 0.25rem 0;
    font-size: 1.2rem;
    font-weight: 700;
}

.section-copy {
    margin: 0;
    color: var(--muted);
    font-size: 0.95rem;
}

.answer-card {
    padding: 1.25rem 1.3rem;
    border-radius: 24px;
    background:
        linear-gradient(145deg, rgba(255, 250, 241, 0.98), rgba(249, 241, 228, 0.92));
    border: 1px solid rgba(195, 91, 44, 0.18);
    box-shadow: var(--shadow);
}

.answer-kicker {
    color: var(--accent-deep);
    font-size: 0.76rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.11em;
}

.answer-body {
    margin-top: 0.7rem;
    font-size: 1.05rem;
    line-height: 1.7;
    color: var(--ink);
}

.pill-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.9rem;
}

.pill {
    padding: 0.35rem 0.65rem;
    border-radius: 999px;
    background: var(--accent-soft);
    color: var(--accent-deep);
    font-size: 0.78rem;
    font-weight: 600;
}

.citation-card {
    padding: 0.95rem 1rem;
    border-radius: 18px;
    background: rgba(255, 255, 255, 0.72);
    border: 1px solid rgba(29, 111, 120, 0.13);
    min-height: 100%;
}

.citation-label {
    color: var(--teal);
    font-size: 0.76rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.citation-text {
    margin-top: 0.55rem;
    color: var(--ink);
    line-height: 1.55;
}

.citation-meta {
    margin-top: 0.8rem;
    color: var(--muted);
    font-size: 0.82rem;
}

.empty-state {
    padding: 1.2rem 1.25rem;
    border-radius: 22px;
    background: rgba(255, 250, 241, 0.84);
    border: 1px dashed rgba(29, 111, 120, 0.24);
    color: var(--muted);
}

[data-testid="stMetric"] {
    background: rgba(255, 251, 245, 0.75);
    border: 1px solid rgba(24, 32, 40, 0.08);
    padding: 0.75rem 0.9rem;
    border-radius: 18px;
}

.stButton > button {
    border-radius: 999px;
    border: 1px solid rgba(125, 51, 22, 0.16);
    background: linear-gradient(135deg, #d56735, #b14f25);
    color: white;
    font-weight: 700;
    letter-spacing: 0.01em;
    box-shadow: 0 10px 20px rgba(177, 79, 37, 0.16);
}

.stButton > button:hover {
    border-color: rgba(125, 51, 22, 0.24);
    background: linear-gradient(135deg, #bf5b2d, #96411d);
}

.stTextInput input, .stNumberInput input, .stTextArea textarea {
    border-radius: 16px !important;
    border: 1px solid rgba(24, 32, 40, 0.12) !important;
    background: rgba(255, 252, 247, 0.95) !important;
}

@media (max-width: 900px) {
    .hero-title {
        font-size: 2.35rem;
    }
    .mini-grid {
        grid-template-columns: 1fr;
    }
}
</style>
"""


def _init_service() -> GraphRAGService:
    settings = get_settings()
    return GraphRAGService.from_settings(settings)


def _format_source_label(path_value: str) -> str:
    path = Path(path_value)
    return path.name or str(path)


def _render_hero(service: GraphRAGService) -> None:
    st.markdown(
        f"""
        <section class="hero-shell">
            <span class="eyebrow">Analyst Workspace</span>
            <h1 class="hero-title">Cybersecurity GraphRAG Assistant</h1>
            <p class="hero-copy">
                Blend your uploaded reports with a built-in cybersecurity corpus, then ask grounded questions
                over indexed evidence, extracted entities, and hybrid retrieval results.
            </p>
            <div class="mini-grid">
                <div class="mini-card">
                    <div class="mini-label">Indexed Chunks</div>
                    <div class="mini-value">{service.document_count}</div>
                </div>
                <div class="mini-card">
                    <div class="mini-label">Graph Engine</div>
                    <div class="mini-value">{"Neo4j" if service.settings.use_neo4j else "Local Fallback"}</div>
                </div>
                <div class="mini-card">
                    <div class="mini-label">Storage Mode</div>
                    <div class="mini-value">{html.escape(service.settings.storage_backend.upper())}</div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _render_section_intro(title: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="section-card">
            <div class="section-title">{html.escape(title)}</div>
            <p class="section-copy">{html.escape(copy)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_answer_card(response: dict, top_result: dict) -> None:
    matched_topics = top_result.get("matched_entities") or []
    pill_markup = "".join(
        f'<span class="pill">{html.escape(topic)}</span>' for topic in matched_topics[:8]
    )
    pill_row = f'<div class="pill-row">{pill_markup}</div>' if pill_markup else ""
    st.markdown(
        f"""
        <div class="answer-card">
            <div class="answer-kicker">
                Grounded Answer · {html.escape(response['confidence'].title())} Confidence ·
                {html.escape(response['answer_mode'].title())} Mode
            </div>
            <div class="answer-body">{html.escape(response['answer'])}</div>
            {pill_row}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_citations(citations: list[dict]) -> None:
    if not citations:
        return
    st.markdown("### Citations")
    columns = st.columns(min(len(citations), 3))
    for index, citation in enumerate(citations):
        column = columns[index % len(columns)]
        label = _format_source_label(citation.get("source_path", "Unknown source"))
        matched = citation.get("matched_entities") or []
        meta_parts = [f"Score {citation['combined_score']:.3f}"]
        if matched:
            meta_parts.append("Entities: " + ", ".join(matched[:5]))
        with column:
            st.markdown(
                f"""
                <div class="citation-card">
                    <div class="citation-label">{html.escape(label)}</div>
                    <div class="citation-text">{html.escape(citation['text'])}</div>
                    <div class="citation-meta">{html.escape(" | ".join(meta_parts))}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def main() -> None:
    st.markdown(APP_CSS, unsafe_allow_html=True)

    if "service" not in st.session_state:
        st.session_state.service = _init_service()
    service: GraphRAGService = st.session_state.service

    with st.sidebar:
        st.markdown("## Control Deck")
        st.write(
            "Curate the assistant from your own reports or from the built-in corpus, then tune how graph and vector evidence are balanced."
        )

        graph_weight = st.slider("Graph weight", 0.0, 1.0, float(service.settings.graph_weight), 0.1)
        vector_weight = st.slider("Vector weight", 0.0, 1.0, float(service.settings.vector_weight), 0.1)
        top_k = st.slider("Results to show", 1, 10, int(service.settings.top_k), 1)
        service.configure_weights(graph_weight=graph_weight, vector_weight=vector_weight)

        st.markdown("### Bring Your Own Sources")
        uploaded_files = st.file_uploader(
            "Upload threat reports, advisories, notes, HTML pages, or PDFs.",
            type=["txt", "md", "markdown", "json", "html", "htm", "pdf"],
            accept_multiple_files=True,
        )

        if st.button("Build from uploads", use_container_width=True):
            if not uploaded_files:
                st.warning("Upload at least one document before building the knowledge base.")
            else:
                with TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    for uploaded_file in uploaded_files:
                        destination = temp_path / uploaded_file.name
                        destination.write_bytes(uploaded_file.getbuffer())
                    with st.spinner("Processing uploaded documents and building the retrieval index..."):
                        count = service.ingest_directory(temp_path)
                st.success(f"Knowledge base updated with {count} document chunk(s).")

        if st.button("Load sample collection", use_container_width=True):
            sample_dir = Path("examples/data")
            with st.spinner("Loading the bundled cybersecurity sample documents..."):
                count = service.ingest_directory(sample_dir)
            st.success(f"Loaded {count} sample document chunk(s).")

        st.markdown("### Built-In Corpus")
        dataset_name = st.text_input(
            "Dataset name",
            value=service.settings.dataset_name,
            help="Hugging Face dataset used as the inbuilt cybersecurity corpus.",
        )
        dataset_split = st.text_input(
            "Dataset split",
            value=service.settings.dataset_split,
            help="Dataset split to ingest, for example train or validation.",
        )
        dataset_limit = st.number_input(
            "Dataset record limit",
            min_value=0,
            value=250,
            step=50,
            help="Use 0 to ingest the full split.",
        )

        if st.button("Load built-in cybersecurity corpus", use_container_width=True):
            with st.spinner("Loading the built-in cybersecurity corpus..."):
                count = service.ingest_hf_dataset(
                    dataset_name=dataset_name.strip() or service.settings.dataset_name,
                    split=dataset_split.strip() or service.settings.dataset_split,
                    limit=None if dataset_limit == 0 else int(dataset_limit),
                )
            st.success(f"Loaded {count} document chunk(s) from the built-in corpus.")

        if st.button("Clear workspace", use_container_width=True):
            service.reset()
            st.success("Cleared the in-app knowledge base.")

        st.divider()
        st.metric("Indexed chunks", service.document_count)
        st.metric("Graph engine", "Neo4j" if service.settings.use_neo4j else "Fallback")
        st.metric("Storage", service.settings.storage_backend.upper())

    _render_hero(service)
    st.write("")

    intro_left, intro_right = st.columns([1.2, 1])
    with intro_left:
        _render_section_intro(
            "Ask grounded cyber questions",
            "The assistant answers from indexed evidence, then surfaces citations and supporting retrieval paths so you can inspect why a result appeared.",
        )
    with intro_right:
        _render_section_intro(
            "Two ways to build context",
            "Upload your own files for organization-specific knowledge, or bootstrap fast with the built-in cybersecurity corpus before layering your own sources on top.",
        )

    st.write("")
    st.markdown("### Query Console")
    query = st.text_input(
        "Type a cybersecurity question about the indexed documents",
        placeholder="For example: Which controls help reduce phishing and credential theft?",
    )

    if st.button("Run analysis", type="primary", use_container_width=True):
        if not query.strip():
            st.warning("Enter a question to search the knowledge base.")
        elif service.document_count == 0:
            st.warning(
                "Build the knowledge base first by uploading files, loading the sample collection, "
                "or loading the built-in cybersecurity corpus."
            )
        else:
            with st.spinner("Searching the knowledge base..."):
                response = service.ask(query, top_k=top_k)
                results = response["results"]

            if not results:
                st.markdown(
                    """
                    <div class="empty-state">
                        No relevant evidence was found for that question yet. Try loading more material or ask
                        with terms like CVE IDs, attack techniques, or control names.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                top_result = results[0]
                _render_answer_card(response, top_result)
                st.write("")

                summary_left, summary_right = st.columns([1.3, 1])
                with summary_left:
                    st.markdown("### Best Match")
                    st.markdown(
                        f"""
                        <div class="section-card">
                            <div class="section-copy" style="color:#182028; line-height:1.7;">
                                {html.escape(top_result["text"])}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with summary_right:
                    st.markdown("### Retrieval Snapshot")
                    st.metric("Top score", f"{top_result['combined_score']:.3f}")
                    st.metric("Sources", ", ".join(top_result.get("retrieval_sources", [])))
                    if top_result.get("matched_entities"):
                        st.write("Matched entities: " + ", ".join(top_result["matched_entities"]))
                    if top_result.get("source_path"):
                        st.caption(f"Source file: {top_result['source_path']}")

                st.write("")
                _render_citations(response["citations"])

                st.write("")
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
    elif service.document_count == 0:
        st.markdown(
            """
            <div class="empty-state">
                Start by uploading your own documents, loading the sample collection, or importing the built-in
                cybersecurity corpus from the sidebar. Once the knowledge base is indexed, this area will show
                grounded answers, citations, and supporting retrieval evidence.
            </div>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
