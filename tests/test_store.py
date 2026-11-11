import pytest

from src.store import KnowledgeStore


def test_add_document_persists_entities_and_relationship_evidence(tmp_path):
    store = KnowledgeStore(str(tmp_path / "graph.db"))
    try:
        text = "Python uses NetworkX to build a knowledge graph."
        edges = [{
            "source": "NetworkX",
            "target": "Python",
            "label": "USES",
            "evidence": text,
            "count": 1,
        }]
        assert store.add_document("notes.md", text, ["Python", "NetworkX", "Python"], edges) is True
        assert store.stats() == {"documents": 1, "entities": 2, "relationships": 1}
        assert {row["name"] for row in store.all_entities()} == {"Python", "NetworkX"}
        assert store.all_relationships()[0]["evidence"] == text
    finally:
        store.close()


def test_duplicate_document_does_not_increment_graph_counts(tmp_path):
    store = KnowledgeStore(str(tmp_path / "graph.db"))
    try:
        text = "Python uses NetworkX to build a knowledge graph."
        edges = [{"source": "Python", "target": "NetworkX", "label": "USES", "evidence": text}]
        assert store.add_document("notes.md", text, ["Python", "NetworkX"], edges) is True
        assert store.add_document("notes.md", text, ["Python", "NetworkX"], edges) is False
        assert store.stats() == {"documents": 1, "entities": 2, "relationships": 1}
        assert all(row["mentions"] == 1 for row in store.all_entities())
        assert store.all_relationships()[0]["count"] == 1
    finally:
        store.close()


def test_relationship_without_source_evidence_is_rejected_before_write(tmp_path):
    store = KnowledgeStore(str(tmp_path / "graph.db"))
    try:
        with pytest.raises(ValueError, match="not present in the source text"):
            store.add_document(
                "bad.md",
                "Python uses NetworkX.",
                ["Python", "NetworkX"],
                [{"source": "Python", "target": "NetworkX", "label": "USES", "evidence": "Invented source quote"}],
            )
        assert store.stats() == {"documents": 0, "entities": 0, "relationships": 0}
    finally:
        store.close()


def test_relationship_must_reference_entities_in_the_same_document(tmp_path):
    store = KnowledgeStore(str(tmp_path / "graph.db"))
    try:
        with pytest.raises(ValueError, match="entity not in this document"):
            store.add_document(
                "bad.md",
                "Python uses NetworkX.",
                ["Python"],
                [{"source": "Python", "target": "NetworkX", "label": "USES", "evidence": "Python uses NetworkX."}],
            )
        assert store.stats() == {"documents": 0, "entities": 0, "relationships": 0}
    finally:
        store.close()


def test_relationship_counts_must_be_positive_integers(tmp_path):
    store = KnowledgeStore(str(tmp_path / "graph.db"))
    try:
        with pytest.raises(ValueError, match="positive integer"):
            store.add_document(
                "bad.md",
                "Python uses NetworkX.",
                ["Python", "NetworkX"],
                [{"source": "Python", "target": "NetworkX", "label": "USES", "evidence": "Python uses NetworkX.", "count": True}],
            )
        assert store.stats() == {"documents": 0, "entities": 0, "relationships": 0}
    finally:
        store.close()
