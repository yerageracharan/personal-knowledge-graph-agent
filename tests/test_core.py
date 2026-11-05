from src.extraction import extract_entities, extract_relationships
from src.search import retrieve

def test_extracts_named_entities_and_acronyms():
    text = "Python works with NetworkX. NASA studies rocket engines."
    entities = extract_entities(text)
    assert any("Python" in e for e in entities)
    assert any("NASA" in e for e in entities)

def test_relationships_keep_evidence():
    text = "Python uses NetworkX to build a knowledge graph."
    entities = extract_entities(text)
    edges = extract_relationships(text, entities)
    assert edges
    assert all(edge["evidence"] for edge in edges)

def test_retrieval_returns_relevant_source():
    docs = [{"name": "notes.md", "text": "Python is used to build data tools. NetworkX stores graph relationships."}]
    results = retrieve("NetworkX graph relationships", docs)
    assert results
    assert results[0]["source"] == "notes.md"
