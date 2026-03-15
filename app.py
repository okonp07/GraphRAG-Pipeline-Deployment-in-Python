"""Landing page for the multipage cybersecurity GraphRAG app."""

from __future__ import annotations

import streamlit as st

from src.frontend import get_service, init_page, render_hero, render_section_intro, render_sidebar_nav


init_page("Cybersecurity GraphRAG Assistant")
service = get_service()
render_sidebar_nav(service)

render_hero(
    service,
    eyebrow="Overview",
    title="Cybersecurity GraphRAG Assistant",
    copy="A multipage analyst workspace for building a cyber knowledge base, tuning hybrid retrieval, and asking grounded questions with citations.",
)
st.write("")

intro_left, intro_right = st.columns([1.2, 1])
with intro_left:
    render_section_intro(
        "Start with the Knowledge Base page",
        "Upload local documents, load the sample collection, or bootstrap the app with the built-in cybersecurity corpus.",
    )
with intro_right:
    render_section_intro(
        "Then move to Ask Assistant",
        "Run grounded analysis over the indexed material and inspect supporting citations, matched entities, and retrieval scores.",
    )

st.write("")
st.markdown("### Workspace Map")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("#### Ask Assistant")
    st.write("Question answering, grounded responses, citations, and ranked supporting evidence.")
    st.page_link("pages/1_Ask_Assistant.py", label="Open Ask Assistant", icon="🧠")
with col2:
    st.markdown("#### Knowledge Base")
    st.write("Uploads, sample data, built-in corpus loading, and workspace maintenance.")
    st.page_link("pages/2_Knowledge_Base.py", label="Open Knowledge Base", icon="📚")
with col3:
    st.markdown("#### Retrieval Settings")
    st.write("Session-level tuning for graph weight, vector weight, and result depth.")
    st.page_link("pages/3_Retrieval_Settings.py", label="Open Retrieval Settings", icon="🎛️")

st.info("Use the page links above or the sidebar Mission Control links to move between workspaces.")
