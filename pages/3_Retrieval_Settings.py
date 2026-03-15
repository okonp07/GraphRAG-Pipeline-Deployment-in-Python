from __future__ import annotations

import streamlit as st

from src.frontend import (
    get_runtime_value,
    get_service,
    init_page,
    render_hero,
    render_section_intro,
    render_sidebar_nav,
)


init_page("Retrieval Settings")
service = get_service()
render_sidebar_nav(service)

render_hero(
    service,
    eyebrow="Settings",
    title="Tune how the assistant retrieves evidence",
    copy="Control the balance between graph signals and vector similarity, adjust result depth, and review runtime details for the current workspace.",
)
st.write("")

intro_left, intro_right = st.columns(2)
with intro_left:
    render_section_intro(
        "Graph weight",
        "Increase this when entity relationships and exact cybersecurity concepts should influence ranking more strongly.",
    )
with intro_right:
    render_section_intro(
        "Vector weight",
        "Increase this when semantic similarity should dominate, especially for more descriptive natural-language queries.",
    )

st.write("")
control_left, control_right = st.columns([1.1, 0.9])
with control_left:
    st.markdown("### Retrieval Controls")
    graph_weight = st.slider(
        "Graph weight",
        0.0,
        1.0,
        float(get_runtime_value("graph_weight", service.settings.graph_weight)),
        0.1,
        key="settings_graph_weight",
    )
    vector_weight = st.slider(
        "Vector weight",
        0.0,
        1.0,
        float(get_runtime_value("vector_weight", service.settings.vector_weight)),
        0.1,
        key="settings_vector_weight",
    )
    top_k = st.slider(
        "Results to show",
        1,
        10,
        int(get_runtime_value("top_k", service.settings.top_k)),
        1,
        key="settings_top_k",
    )
    st.session_state["graph_weight"] = graph_weight
    st.session_state["vector_weight"] = vector_weight
    st.session_state["top_k"] = top_k
    service.configure_weights(graph_weight=graph_weight, vector_weight=vector_weight)
    st.success("Runtime retrieval settings updated for this session.")

with control_right:
    st.markdown("### Runtime Summary")
    st.metric("Indexed chunks", service.document_count)
    st.metric("Storage backend", service.settings.storage_backend.upper())
    st.metric("Graph engine", "Neo4j" if service.settings.use_neo4j else "Fallback")
    st.caption(
        "These controls affect the current app session. You can use them to compare retrieval behavior before deciding on permanent defaults."
    )

st.write("")
st.markdown("### Configuration Notes")
st.write(
    "For stable environment defaults, update the settings in `config.py` or the corresponding `GRAPHRAG_*` environment variables. Use this page as a lightweight tuning lab before locking those values in."
)
