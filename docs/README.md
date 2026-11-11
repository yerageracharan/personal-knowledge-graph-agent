# Documentation map

Start with the [project README](../README.md) for the product overview, installation, provider setup, Streamlit workflow, MCP connection, privacy model, and limitations.

## User and operator guides

- [Provider setup](PROVIDERS.md) — configure hosted APIs, local Ollama/LM Studio endpoints, or no-LLM heuristic mode.
- [Dependency and runtime policy](dependency-policy.md) — supported Python versions, NetworkX compatibility, and dependency update procedure.
- [Knowledge ingestion pipeline](visuals/01-knowledge-pipeline.svg) — document-to-graph workflow.
- [Retrieval loop](visuals/02-retrieval-loop.svg) — query-to-source-evidence workflow.

## Code ownership map

| Area | Source of truth | Responsibility |
|---|---|---|
| Streamlit UI | `app.py` | Upload, configuration, graph visualisation, user interaction |
| Document ingestion | `src/ingestion.py` | File parsing and text preparation |
| Entity and edge extraction | `src/extraction.py` | Candidate graph facts and evidence |
| Optional model adapters | `src/llm.py` | Provider-specific model calls |
| Search and ranking | `src/search.py` | Local TF-IDF retrieval |
| Application services | `src/service.py` | Orchestration between UI, extraction, storage, and retrieval |
| Persistence | `src/store.py` | SQLite source of truth for documents, entities, and relationships |
| AI assistant interface | `mcp_server.py` | Local MCP tool boundary |
| Regression coverage | `tests/` | Core behavior, provider adapters, and persistence contracts |

## Engineering and governance

- [Contribution workflow](../CONTRIBUTING.md)
- [AI coding-agent instructions](../AGENTS.md)
- [Security and data-handling policy](../SECURITY.md)
- [Automated tests](../tests/)
- [Dependency automation](../.github/dependabot.yml)

Use synthetic documents in tests. Do not commit private notes, uploaded documents, tokens, or local SQLite databases.
