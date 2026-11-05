# Model providers and MCP integrations

This project has two separate integration paths:

1. **Direct model providers** power extraction and answer synthesis inside the app.
2. **MCP tools** expose your knowledge base to compatible AI assistants.

## Direct provider configuration

Set these environment variables or use the Streamlit sidebar:
- `LLM_PROVIDER`: `openai`, `anthropic`, `ollama`, `openai-compatible`, or `none`
- `LLM_MODEL`: exact model ID accepted by your provider
- `LLM_API_KEY`: provider key (not needed for local Ollama)
- `LLM_BASE_URL`: optional OpenAI-compatible API base URL

| Provider | Provider value | Base URL | Model example |
|---|---|---|---|
| OpenAI | `openai` | blank | `gpt-4o-mini` |
| Anthropic | `anthropic` | unused | provider-supported Claude model ID |
| Ollama | `ollama` | `http://localhost:11434/v1` | `llama3.1` |
| LM Studio / vLLM / compatible gateway | `openai-compatible` | your server's `/v1` URL | served model ID |

Any OpenAI-compatible endpoint can be used if it implements the Chat Completions API. Other proprietary API formats need a dedicated adapter. Credentials are passed at runtime and are not written to SQLite or committed to Git.

### Ollama

Install Ollama, pull a model, then configure provider `ollama`, base URL `http://localhost:11434/v1`, and the exact model name shown by Ollama. No hosted API key is needed.

### Environment file

Copy `.env.example` to `.env`, then fill in the values. The app loads this file automatically. Never commit the real `.env`.

## MCP tools

The server exposes:
- `add_text_document`
- `search_knowledge`
- `ask_knowledge`
- `get_knowledge_graph`
- `list_knowledge_sources`

### Claude Desktop — local Windows setup

1. Install dependencies and test the server from the repository folder:
   ```powershell
   .venv\Scripts\Activate.ps1
   python mcp_server.py
   ```
   Stop it with Ctrl+C after confirming it starts.
2. Open Claude Desktop's developer configuration file. On Windows it is normally under `%AppData%\Claude\claude_desktop_config.json`.
3. Add this server entry, replacing the paths with your actual absolute paths:
   ```json
   {
     "mcpServers": {
       "personal-knowledge-graph": {
         "command": "C:\\Users\\YOUR_USER\\personal-knowledge-graph-agent\\.venv\\Scripts\\python.exe",
         "args": ["C:\\Users\\YOUR_USER\\personal-knowledge-graph-agent\\mcp_server.py"]
       }
     }
   }
   ```
4. Restart Claude Desktop. Check Settings / Developer or the tools menu for the connected server.

Claude Desktop supports local MCP servers. Claude's desktop extensions can also package local MCP servers for easier installation; this repository does not yet include a packaged extension.

### ChatGPT

ChatGPT does not connect directly to a local stdio MCP process. Current options are:

- **Secure MCP Tunnel:** keep this MCP server running locally and use OpenAI's Secure MCP Tunnel client to make it reachable to supported OpenAI products without publishing your database server.
- **Remote HTTPS MCP:** deploy the server on a host you control. For private personal data, implement OAuth 2.1 authentication and authorization before exposing it. Do not publish the current unauthenticated HTTP mode to the public internet.
- **OpenAI API:** an application using the OpenAI Responses API can call remote MCP servers, separately from a ChatGPT subscription. API usage is billed separately.

**ChatGPT account availability matters:** current OpenAI help documentation lists custom MCP app connections for Business and Enterprise/Edu workspaces; Pro has more limited read/fetch access in developer mode. Go is not listed as having custom MCP app connections in that guidance. Check the current Help Center before planning around ChatGPT's in-product MCP UI.

This repo currently implements local stdio MCP for Claude Desktop and a Streamable HTTP transport for development. It does **not** yet implement OAuth 2.1 or production-grade remote authentication. Use local Claude integration first; do not expose personal documents over unauthenticated HTTP.

## Privacy and limitations

- Local-only mode keeps documents and the SQLite database on your machine.
- When a hosted LLM is enabled, relevant document text is sent to that provider for extraction or answer generation.
- Ollama can keep model inference local when the Ollama server itself runs on your machine.
- MCP clients can read or add data through the tools you expose.
- Graph relationships are candidates supported by source text, not automatically verified facts.
- Search currently uses local TF-IDF retrieval, not vector embeddings or true graph multi-hop retrieval.
- Scanned PDFs require OCR; OCR is not included yet.
