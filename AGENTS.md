# Agent Instructions

These instructions apply across Personal Knowledge Graph Agent.

## Product invariants

- Every extracted entity and relationship must preserve the source document and evidence text that supports it.
- Do not invent facts or relationships when the source is ambiguous; label uncertain extraction or omit it.
- Keep the SQLite document/entity/relationship update atomic and validate all relationships before writing.
- Search results must be bounded, source-linked, and explicit about retrieval limitations.
- Local processing is the default; any external-model path must be explicit about where document content is sent.

## Repository map

- `src/`: document ingestion, extraction, SQLite persistence, and retrieval.
- `app.py`: Streamlit interface.
- `mcp_server.py`: local MCP interface.
- `docs/`: provider setup and product documentation.
- `tests/`: deterministic extraction, storage, and search tests.

## Working rules

- Read the storage schema and callers before changing persistence behavior.
- Validate entity references, evidence spans, and counts before a transaction begins.
- Preserve the existing source reference when changing extraction or search result schemas.
- Never use a real personal document in a committed fixture or screenshot.
- Keep local/offline behavior clear; disclose external provider data transfer in docs and UI.
- Bound result counts and input sizes. Do not return the entire knowledge base by default.
- If schema migrations are introduced, include an upgrade path and rollback strategy.

## Validation

```bash
python -m pytest -q
```
