"""Streamlit UI for a local-first, provider-independent personal knowledge graph."""
import os
import networkx as nx
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network

from src.llm import LLMConfig
from src.service import KnowledgeService

st.set_page_config(page_title="Personal Knowledge Graph Agent", page_icon="🧠", layout="wide")
st.title("Personal Knowledge Graph Agent")
st.caption("Your documents, connected. Choose a model provider—or run entirely locally without one.")

with st.sidebar:
    st.header("Model settings")
    default_provider=os.getenv("LLM_PROVIDER","none")
    providers=["none","openai","anthropic","ollama","openai-compatible"]
    provider=st.selectbox("LLM provider",providers,index=providers.index(default_provider) if default_provider in providers else 0,
        help="Choose none for local heuristic extraction and retrieval.")
    env_model=os.getenv("LLM_MODEL","")
    model=st.text_input("Model ID",value=env_model,placeholder="e.g. gpt-4o-mini, claude model ID, llama3.1")
    env_url=os.getenv("LLM_BASE_URL","")
    base_url=st.text_input("API base URL (for Ollama or compatible APIs)",value=env_url,
        placeholder="http://localhost:11434/v1")
    env_key=os.getenv("LLM_API_KEY","")
    api_key=st.text_input("API key",value=env_key,type="password",
        help="Kept in this Streamlit session; do not commit API keys.")
    st.caption("For Ollama, leave the API key blank. For ChatGPT/Claude assistant integrations, see docs/PROVIDERS.md.")
    config=LLMConfig(provider=provider,model=model,api_key=api_key,base_url=base_url)
    st.divider()
    st.header("Add knowledge")
    uploads=st.file_uploader("Upload TXT, Markdown or PDF",type=["txt","md","pdf"],accept_multiple_files=True)
    if st.button("Process documents",type="primary",disabled=not uploads):
        service=KnowledgeService(llm_config=config)
        progress=st.progress(0)
        for i,file in enumerate(uploads):
            try:
                result=service.ingest(file.name,file.getvalue())
                if result["added"]:
                    st.success(f'{file.name}: {result["entities"]} entities, {result["relationships"]} relationships ({result["extraction"]})')
                else:
                    st.info(f"{file.name}: already indexed; rename it to ingest a revised copy.")
            except Exception as exc:
                st.error(f"{file.name}: {exc}")
            progress.progress((i+1)/len(uploads))

service=KnowledgeService(llm_config=config)
stats=service.store.stats()
cols=st.columns(3)
for col,(label,value) in zip(cols,stats.items()): col.metric(label.title(),value)

tab_graph,tab_ask,tab_data,tab_sources=st.tabs(["Knowledge graph","Ask your knowledge","Entities & relationships","Sources"])
with tab_graph:
    graph_data=service.graph()
    if not graph_data["entities"]:
        st.info("Upload a few documents to build your first graph.")
    else:
        graph=nx.Graph()
        for entity in graph_data["entities"]: graph.add_node(entity["name"],mentions=entity["mentions"])
        for edge in graph_data["relationships"]:
            graph.add_edge(edge["source"],edge["target"],label=edge["label"],title=edge["evidence"])
        net=Network(height="640px",width="100%",bgcolor="#0e1117",font_color="white",notebook=False)
        net.from_nx(graph)
        for node in net.nodes:
            count=graph.nodes[node["label"]].get("mentions",1)
            node["title"]=f'{node["label"]} · mentions: {count}'
            node["size"]=12+min(30,count*3)
        for edge in net.edges: edge["title"]=edge.get("label","RELATED")
        components.html(net.generate_html(),height=660,scrolling=True)
        st.caption("Edges are candidate relationships, not guaranteed facts. Inspect their source evidence in the relationships tab.")

with tab_ask:
    st.write(f"Active model: **{provider}**" + (f" / {model}" if model else " (retrieval-only mode)"))
    question=st.text_input("Ask a question about your documents",placeholder="What connects my AI projects and the tools I use?")
    if st.button("Ask",type="primary",disabled=not question.strip()):
        with st.spinner("Searching your knowledge..."):
            result=service.ask(question)
        st.markdown(result["answer"])
        st.caption(f'Response mode: {result.get("mode","retrieval")}')
        with st.expander("Retrieved source evidence",expanded=True):
            for i,item in enumerate(result.get("evidence",[]),1):
                st.markdown(f'**[{i}] {item["source"]}** · relevance {item["score"]:.3f}')
                st.write(item["text"])

with tab_data:
    left,right=st.columns(2)
    with left:
        st.subheader("Entities")
        st.dataframe(graph_data["entities"],use_container_width=True,hide_index=True)
    with right:
        st.subheader("Relationships and evidence")
        st.dataframe(graph_data["relationships"],use_container_width=True,hide_index=True)

with tab_sources:
    st.subheader("Indexed documents")
    docs=service.store.documents()
    if docs: st.dataframe([dict(x) for x in docs],use_container_width=True,hide_index=True)
    else: st.info("No documents indexed yet.")
    st.caption("Database: data/knowledge.db. Your document files and database stay local unless you send text to a configured hosted model.")
