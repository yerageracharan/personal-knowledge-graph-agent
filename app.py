"""Streamlit interface for the Personal Knowledge Graph Agent."""
from pathlib import Path
import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

from src.ingestion import extract_text
from src.extraction import extract_entities, extract_relationships
from src.store import KnowledgeStore
from src.search import retrieve

st.set_page_config(page_title="Personal Knowledge Graph", page_icon="🧠", layout="wide")
st.title("Personal Knowledge Graph Agent")
st.caption("Turn scattered documents into connected, searchable knowledge. Runs locally; no API key required.")

@st.cache_resource
def get_store():
    return KnowledgeStore()
store = get_store()

with st.sidebar:
    st.header("Add knowledge")
    uploads = st.file_uploader("Upload TXT, Markdown or PDF files", type=["txt", "md", "pdf"], accept_multiple_files=True)
    if st.button("Process documents", type="primary", disabled=not uploads):
        added, skipped = 0, 0
        progress = st.progress(0)
        for i, file in enumerate(uploads):
            try:
                text = extract_text(file.name, file.getvalue())
                if not text:
                    st.warning(f"No extractable text found in {file.name}")
                    continue
                entities = extract_entities(text)
                edges = extract_relationships(text, entities)
                if store.add_document(file.name, text, entities, edges):
                    added += 1
                else:
                    skipped += 1
            except Exception as exc:
                st.error(f"{file.name}: {exc}")
            progress.progress((i + 1) / len(uploads))
        st.success(f"Added {added} document(s); skipped {skipped} duplicate(s).")

stats = store.stats()
cols = st.columns(3)
for col, (label, value) in zip(cols, stats.items()):
    col.metric(label.title(), value)

tab_graph, tab_search, tab_entities, tab_sources = st.tabs(["Knowledge graph", "Ask your knowledge", "Entities & relations", "Sources"])
with tab_graph:
    edges = store.all_relationships()
    entities = store.all_entities()
    if not entities:
        st.info("Upload a few documents to start building your graph.")
    else:
        graph = nx.Graph()
        for e in entities:
            graph.add_node(e["name"], mentions=e["mentions"])
        for edge in edges:
            graph.add_edge(edge["source"], edge["target"], label=edge["label"])
        net = Network(height="620px", width="100%", bgcolor="#0e1117", font_color="white", notebook=False)
        net.from_nx(graph)
        for node in net.nodes:
            node["title"] = f'{node["label"]} · mentions: {graph.nodes[node["label"]].get("mentions", 1)}'
            node["size"] = 12 + min(25, graph.nodes[node["label"]].get("mentions", 1) * 3)
        for edge in net.edges:
            edge["title"] = edge.get("label", "MENTIONED_WITH")
        html = net.generate_html()
        components.html(html, height=640, scrolling=True)

with tab_search:
    question = st.text_input("What do you want to know?", placeholder="How are Python and the knowledge graph connected?")
    if st.button("Search knowledge") and question:
        results = retrieve(question, store.get_document_texts())
        if not results:
            st.warning("No matching evidence found. Try different keywords or add more documents.")
        for result in results:
            st.markdown(f'**{result["source"]}** · relevance {result["score"]:.2f}')
            st.write(result["text"])
            st.divider()
    st.caption("Answers are evidence snippets ranked by local TF-IDF retrieval, not generated claims.")

with tab_entities:
    left, right = st.columns(2)
    with left:
        st.subheader("Entities")
        st.dataframe([dict(x) for x in store.all_entities()], use_container_width=True, hide_index=True)
    with right:
        st.subheader("Relationships")
        st.dataframe([dict(x) for x in store.all_relationships()], use_container_width=True, hide_index=True)

with tab_sources:
    st.subheader("Indexed documents")
    docs = store.documents()
    if docs:
        st.dataframe([dict(x) for x in docs], use_container_width=True, hide_index=True)
    else:
        st.info("No documents indexed yet.")
    st.caption("Local database: data/knowledge.db")
