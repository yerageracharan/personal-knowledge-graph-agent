# Personal Knowledge Graph Agent

> **Agent #7 / 200 AI Agents in 200 Days**  
> Turn scattered notes and documents into a connected, searchable map of knowledge.

A local-first knowledge assistant that ingests TXT, Markdown and PDF files, extracts candidate entities and relationships, stores them in SQLite, visualises a graph, and retrieves evidence from your own documents.

## What it does

- **Ingest:** upload TXT, Markdown and text-based PDF documents.
- **Extract:** detect candidate people, organisations, technologies, concepts and acronyms using transparent local heuristics.
- **Connect:** create relationships when entities appear together in the same sentence; detect a small set of explicit relation phrases.
- **Visualise:** explore the resulting network.
- **Search:** retrieve relevant evidence snippets from your documents using local TF-IDF.
- **Keep control:** data stays in the local `data/` folder. No API key or hosted service is required.

## Quick start

Python 3.10+ recommended.

```bash
git clone https://github.com/yerageracharan/personal-knowledge-graph-agent.git
cd personal-knowledge-graph-agent

python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit, upload a few documents, and explore the graph.

## Run tests

```bash
pytest -q
```

## Architecture

```text
Documents (TXT / MD / PDF)
          |
          v
   Text extraction
          |
          v
 Candidate entity extraction
          |
          v
 Relationship discovery
          |
          v
 SQLite knowledge store
       /       \
      v         v
 Graph view   TF-IDF retrieval
                  |
                  v
          Evidence snippets
```

## Project structure

```text
app.py                 Streamlit UI
src/ingestion.py       TXT, Markdown and PDF extraction
src/extraction.py      Candidate entities and relationships
src/store.py           SQLite persistence
src/search.py          Local TF-IDF evidence retrieval
tests/test_core.py     Core tests
```

## Important limitations

This is a transparent baseline, not a fully autonomous reasoning system yet.

- Entity extraction uses heuristics; it can miss names and may produce false positives.
- Co-occurrence is not proof of a real-world relationship. Every edge stores its supporting sentence so you can inspect it.
- The search module retrieves evidence; it does not generate free-form answers.
- Scanned PDFs need OCR before their text can be indexed.
- The first version does not sync data to the cloud.

**Design principle:** prefer traceable evidence over confident-sounding guesses. Treat extracted nodes and edges as candidates for review.

## Roadmap

- [x] Local document ingestion
- [x] Candidate entity and relation extraction
- [x] SQLite persistence
- [x] Interactive graph visualisation
- [x] Evidence-based retrieval
- [ ] Entity deduplication and alias resolution
- [ ] User-reviewed edge confirmation
- [ ] Optional local LLM for structured extraction and answer synthesis
- [ ] Graph-aware multi-hop retrieval
- [ ] Export graph as JSON / GraphML

## Agent challenge

**Agent #7 of 200.** The aim is to learn practical information extraction, graph modelling, retrieval, evaluation and agent workflow design by shipping a working tool.

Built by [@yerageracharan](https://github.com/yerageracharan).
