# Personal Knowledge Graph Agent

> **Agent #7 / 200 AI Agents in 200 Days**  
> Your documents, connected. A local-first knowledge graph that works with multiple LLM providers and exposes tools to ChatGPT and Claude through MCP.

Turn PDFs, Markdown and text files into an evidence-backed graph of entities and relationships. Use a hosted model, a local open-source model, an OpenAI-compatible API, or no LLM at all.

## What it does

- **Ingest:** PDF, TXT and Markdown documents.
- **Extract:** candidate entities and relationships using local heuristics or an LLM.
- **Validate:** LLM-generated edges are accepted only when their evidence is an exact sentence from the source document.
- **Visualise:** explore the graph in an interactive browser view.
- **Ask:** retrieve relevant passages and optionally synthesize an answer with source citations.
- **Integrate:** expose the knowledge base as MCP tools for compatible AI assistants.
- **Stay portable:** SQLite storage; provider adapters are swappable.

## Quick start — Windows

Python 3.10+ recommended.

```powershell
git clone https://github.com/yerageracharan/personal-knowledge-graph-agent.git
cd personal-knowledge-graph-agent
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Open the local Streamlit URL. Upload a few documents and explore the graph.

## Choose your model

Use the sidebar in the app to select a provider. The app does not require an LLM: choose `none` for local heuristic extraction and retrieval.

| Provider | Provider setting | Model example | Notes |
|---|---|---|---|
| OpenAI | `openai` | `gpt-4o-mini` | Requires OpenAI API key |
| Anthropic | `anthropic` | `claude-3-5-haiku-latest` | Uses Anthropic Messages API |
| Ollama | `ollama` | `llama3.1` | Local model; no hosted API key |
| LM Studio / vLLM / compatible gateway | `openai-compatible` | Server's model ID | Any OpenAI Chat Completions-compatible endpoint |
| No model | `none` | — | Offline baseline |

For persistent defaults, copy `.env.example` to `.env` and fill in the values. Do not commit `.env` or API keys.

Example for a local Ollama server:
```env
LLM_PROVIDER=ollama
LLM_MODEL=llama3.1
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=
```

For a custom OpenAI-compatible API:
```env
LLM_PROVIDER=openai-compatible
LLM_MODEL=your-model-id
LLM_BASE_URL=https://your-provider.example/v1
LLM_API_KEY=your-api-key
```

Provider setup and assistant integration details: [docs/PROVIDERS.md](docs/PROVIDERS.md).

## Connect it to Claude or ChatGPT

The project includes an MCP server exposing:
- `add_text_document`
- `search_knowledge`
- `ask_knowledge`
- `get_knowledge_graph`
- `list_knowledge_sources`

Claude Desktop can run it locally over stdio. ChatGPT custom MCP connections require a reachable HTTPS MCP endpoint and an account/workspace with custom MCP app support. See [docs/PROVIDERS.md](docs/PROVIDERS.md) for configuration.

**Important:** MCP is the bridge that lets an assistant call this project's tools. It does not turn a ChatGPT Plus or Claude subscription into an API key for the app's internal model calls.

## Architecture

```text
PDF / TXT / Markdown
        |
        v
   Text extraction
        |
        v
  LLM or heuristic extraction <---- OpenAI / Anthropic / Ollama / compatible API
        |
        v
 Evidence validation + SQLite graph
        |
        +------> Interactive graph UI
        |
        +------> TF-IDF evidence retrieval
        |                 |
        |                 v
        |          Optional LLM answer
        |
        +------> MCP tools <---- ChatGPT / Claude / other MCP clients
```

## Tests

```powershell
pytest -q
```

GitHub Actions runs the test suite on pushes and pull requests.

## Privacy and limitations

- Local mode stores documents and the SQLite database on your machine.
- When using a hosted LLM, relevant document text is sent to that provider for extraction or answer generation.
- Local Ollama keeps inference on your machine, but network exposure depends on your Ollama configuration.
- MCP clients can access the tools you expose. Do not expose a personal knowledge base to the public internet without authentication, authorization and per-user isolation.
- Entity extraction is fallible. Graph edges are candidates with source evidence, not automatically verified facts.
- Scanned PDFs require OCR; OCR is not included yet.
- Search currently uses local TF-IDF retrieval, not a vector database or true graph multi-hop retrieval.

## Roadmap

- [x] TXT / Markdown / PDF ingestion
- [x] SQLite graph persistence
- [x] Interactive graph visualisation
- [x] Local retrieval baseline
- [x] OpenAI and OpenAI-compatible endpoint adapter
- [x] Anthropic adapter
- [x] Ollama / local OpenAI-compatible model support
- [x] MCP tools for assistant integrations
- [ ] Authentication and user isolation for remote MCP deployment
- [ ] Vector embeddings and hybrid retrieval
- [ ] Entity alias resolution and duplicate merging
- [ ] Graph-aware multi-hop question answering
- [ ] OCR for scanned PDFs
- [ ] Graph export (JSON / GraphML)

## Agent challenge

**Agent #7 of 200.** Built to explore information extraction, knowledge representation, LLM abstraction, evidence validation, retrieval and MCP-based interoperability.

Built by [@yerageracharan](https://github.com/yerageracharan).
