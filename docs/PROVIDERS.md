# Model providers and MCP integrations

Two separate paths are supported:

- Direct providers power graph extraction and answer synthesis inside the app.
- MCP exposes your personal knowledge base as tools to compatible assistants.

## Direct provider configuration

Set these environment variables or use the app settings:
- `LLM_PROVIDER`: `openai`, `anthropic`, `ollama`, `openai-compatible`, or `none`
- `LLM_MODEL`: exact model ID accepted by your provider
- `LLM_API_KEY`: provider key (not needed for local Ollama)
- `LLM_BASE_URL`: optional OpenAI-compatible API base URL

Examples:

| Provider | Provider | Base URL | Model example |
|---|---|---|---|
| OpenAI | `openai` | blank | `gpt-4o-mini` |
| Anthropic | `anthropic` | unused | `claude-3-5-haiku-latest` |
| Ollama | `ollama` | `http://localhost:11434/v1` | `llama3.1` |
| LM Studio / vLLM / compatible gateway | `openai-compatible` | your server's `/v1` URL | served model ID |

Any OpenAI-compatible endpoint can be used if it implements Chat Completions. Providers with a different API format need an adapter. Credentials are passed at runtime and are not stored in SQLite.

## Ollama

Install Ollama, pull a model, then configure provider `ollama`, base URL `http://localhost:11434/v1`, and the model name shown by Ollama. No hosted API key is needed.

## MCP tools for Claude and ChatGPT

The MCP server exposes `add_text_document`, `search_knowledge`, `ask_knowledge`, `get_knowledge_graph`, and `list_knowledge_sources`.

### Claude Desktop (local)

Run `python mcp_server.py` from the project virtual environment. Add this to Claude Desktop's MCP configuration, replacing paths with absolute Windows paths:

```json
{
  "mcpServers": {
    "personal-knowledge-graph": {
      "command": "C:\\absolute\\path\\to\\.venv\\Scripts\\python.exe",
      "args": ["C:\\absolute\\path\\to\\mcp_server.py"]
    }
  }
}
```

Restart Claude Desktop and enable the server's tools.

### ChatGPT

Custom MCP app access requires a reachable server and a ChatGPT account/workspace that supports custom MCP connections. For remote use, deploy the server with HTTPS, authentication and persistent storage, then configure its MCP endpoint in ChatGPT's app/developer integration settings. Plan and workspace availability can vary.

### Remote transport

Set `MCP_TRANSPORT=streamable-http` and run `python mcp_server.py`. Do not expose a personal knowledge base publicly without authentication, authorization and per-user storage isolation.

## Privacy

- Local-only mode keeps documents and the SQLite database on your machine.
- When an external LLM is enabled, relevant document text is sent to that provider for processing.
- MCP clients can access the tools you expose. Only connect trusted clients.
- The current MCP server is a local development baseline, not a hardened multi-tenant public service.
