import pytest

from src.extraction import extract_entities, extract_relationships
from src.search import MAX_RESULTS, retrieve


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


@pytest.mark.parametrize("limit", [0, -1, MAX_RESULTS + 1])
def test_retrieval_rejects_out_of_range_limit(limit):
    with pytest.raises(ValueError, match="limit must be between"):
        retrieve("graph", [], limit=limit)


@pytest.mark.parametrize("limit", [True, 1.5, "5"])
def test_retrieval_rejects_non_integer_limit(limit):
    with pytest.raises(TypeError, match="limit must be an integer"):
        retrieve("graph", [], limit=limit)


def test_retrieval_returns_empty_for_blank_query_or_empty_documents():
    assert retrieve("   ", [{"name": "notes.md", "text": "Some useful knowledge graph content."}]) == []
    assert retrieve("graph", []) == []


def test_retrieval_rejects_malformed_document_records():
    with pytest.raises(ValueError, match="string 'name' and 'text'"):
        retrieve("graph", [{"name": "notes.md", "text": None}])


def test_retrieval_handles_punctuation_only_corpus():
    assert retrieve("!!!", [{"name": "notes.md", "text": "!!! ??? ..."}]) == []
