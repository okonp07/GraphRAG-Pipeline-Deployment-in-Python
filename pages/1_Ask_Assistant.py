from __future__ import annotations

import html

import streamlit as st

from src.frontend import (
    format_source_label,
    get_retrieval_state,
    get_service,
    init_page,
    render_answer_card,
    render_citations,
    render_empty_state,
    render_hero,
    render_section_intro,
    render_sidebar_nav,
)


init_page("Ask Assistant")
service = get_service()
_, _, top_k = get_retrieval_state(service)
render_sidebar_nav(service)

render_hero(
    service,
    eyebrow="Ask",
    title="Query your cybersecurity knowledge base",
    copy="Run grounded analysis over uploaded material and the built-in cyber corpus, then inspect citations and supporting retrieval evidence.",
)
st.write("")

intro_left, intro_right = st.columns([1.2, 1])
with intro_left:
    render_section_intro(
        "Grounded answers",
        "Each response is synthesized from retrieved evidence rather than invented in isolation, so you can inspect the supporting passages.",
    )
with intro_right:
    render_section_intro(
        "Built for mixed sources",
        "Combine your own reports with the built-in corpus to answer organization-specific and general cybersecurity questions side by side.",
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
            "Build the knowledge base first from the Knowledge Base page, then return here to ask questions."
        )
    else:
        with st.spinner("Searching the knowledge base..."):
            response = service.ask(query, top_k=top_k)
            results = response["results"]

        if not results:
            render_empty_state(
                "No relevant evidence was found for that question yet. Try loading more material or ask with terms like CVE IDs, attack techniques, or control names."
            )
        else:
            top_result = results[0]
            render_answer_card(response, top_result)
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
            render_citations(response["citations"])

            st.write("")
            st.markdown("### Supporting Results")
            for index, result in enumerate(results, start=1):
                title = f"{index}. {format_source_label(result.get('source_path', 'Unknown source'))}"
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
    render_empty_state(
        "Start from the Knowledge Base page to upload your own documents, load the sample collection, or import the built-in cybersecurity corpus. Then come back here to ask questions."
    )
