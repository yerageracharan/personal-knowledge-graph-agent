"""MCP tools for ChatGPT and Claude. Local default: python mcp_server.py"""
import os
from mcp.server.fastmcp import FastMCP
from src.service import KnowledgeService
mcp=FastMCP("Personal Knowledge Graph")
service=KnowledgeService(os.getenv("KNOWLEDGE_DB","data/knowledge.db"))
@mcp.tool()
def add_text_document(name: str, text: str) -> dict:
    """Add a plain text or Markdown document to the knowledge graph."""
    return service.ingest_text(name,text)
@mcp.tool()
def search_knowledge(query: str, limit: int=6) -> list[dict]:
    """Search indexed documents and return source-grounded evidence."""
    return service.search(query,max(1,min(limit,15)))
@mcp.tool()
def ask_knowledge(question: str) -> dict:
    """Answer a question from indexed knowledge and include supporting source evidence."""
    return service.ask(question)
@mcp.tool()
def get_knowledge_graph() -> dict:
    """Return entities, relationships and graph statistics."""
    return service.graph()
@mcp.tool()
def list_knowledge_sources() -> list[dict]:
    """List indexed source documents."""
    return [dict(row) for row in service.store.documents()]
if __name__=="__main__":
    if os.getenv("MCP_TRANSPORT","stdio")=="streamable-http": mcp.run(transport="streamable-http")
    else: mcp.run()
