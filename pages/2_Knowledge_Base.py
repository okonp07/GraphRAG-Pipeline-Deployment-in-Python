from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import streamlit as st

from src.frontend import (
    get_service,
    init_page,
    render_empty_state,
    render_hero,
    render_section_intro,
    render_sidebar_nav,
)


init_page("Knowledge Base")
service = get_service()
render_sidebar_nav(service)

render_hero(
    service,
    eyebrow="Knowledge Base",
    title="Build and refresh your indexed corpus",
    copy="Load your own reports, bootstrap from a built-in cybersecurity dataset, or start from the bundled sample collection.",
)
st.write("")

top_left, top_right = st.columns([1.1, 1])
with top_left:
    render_section_intro(
        "Bring your own documents",
        "Upload local advisories, incident notes, reports, HTML pages, or PDFs and turn them into a searchable cybersecurity knowledge base.",
    )
with top_right:
    render_section_intro(
        "Use an inbuilt source of truth",
        "Bootstrap the assistant with the default cybersecurity corpus before adding your own organization-specific material on top.",
    )

st.write("")
left, right = st.columns(2)

with left:
    st.markdown("### Upload Documents")
    uploaded_files = st.file_uploader(
        "Supported formats: TXT, MD, Markdown, JSON, HTML, PDF",
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

with right:
    st.markdown("### Built-In Cybersecurity Corpus")
    dataset_name = st.text_input(
        "Dataset name",
        value=service.settings.dataset_name,
        help="Hugging Face dataset used as the built-in cybersecurity corpus.",
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

st.write("")
status_left, status_right = st.columns([1.25, 1])
with status_left:
    st.markdown("### Workspace Status")
    if service.document_count == 0:
        render_empty_state(
            "No knowledge base is loaded yet. Build one from uploads, the sample collection, or the built-in cybersecurity corpus."
        )
    else:
        st.success(f"The workspace currently contains {service.document_count} indexed chunk(s).")
        st.caption(
            "Go to the Ask Assistant page to query the indexed material, or to Retrieval Settings to tune the search balance."
        )
with status_right:
    st.markdown("### Maintenance")
    if st.button("Clear workspace", use_container_width=True):
        service.reset()
        st.success("Cleared the in-app knowledge base.")
