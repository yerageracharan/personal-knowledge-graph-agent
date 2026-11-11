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

## Change ownership and proof

- Keep one authoritative owner for each domain rule and each persisted state. UI, CLI, MCP, and provider adapters translate inputs and outputs; they must not reimplement business policy or become competing sources of truth.
- Before changing a contract, trace the input through its owner to every consumer. Update callers, schemas, examples, docs, and regression tests together. Remove superseded paths unless a documented public-compatibility requirement keeps them.
- Keep optional external model/provider integrations behind adapters. Use injected or mocked adapters for deterministic unit tests; label live network/provider checks separately and never describe a mock as live verification.
- Validate untrusted user, model, file, and network data at the boundary. Preserve the product's evidence/provenance rules and reject malformed inputs rather than silently inventing defaults.
- Verify the supported user entry point and at least one relevant failure path. Report exact commands and results; CI on a different commit SHA is not proof for the current change.
- Keep the root README as the user entry point, `docs/README.md` as the documentation map, and focused guides as the owners of detailed contracts. Update links when files move. Do not hand-edit generated output when a source or generator owns it.
