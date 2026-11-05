"""Lightweight, local entity and relationship extraction.

This deliberately uses transparent heuristics so the first version works offline
without API keys. Treat extracted facts as suggestions, not ground truth.
"""
from __future__ import annotations
import re
from collections import Counter
from typing import Iterable

STOP = {"The", "This", "That", "These", "Those", "When", "Where", "What",
        "Why", "How", "A", "An", "In", "On", "At", "For", "From", "With",
        "As", "It", "He", "She", "They", "We", "I", "But", "And", "Or",
        "However", "Therefore", "If", "After", "Before", "While", "There"}

def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if len(s.strip()) > 20]

def extract_entities(text: str) -> list[str]:
    """Find likely names, acronyms, hashtags and technical terms."""
    candidates = []
    patterns = [
        r"\b[A-Z][a-z]+(?:\s+[A-Z][a-zA-Z0-9&.-]+){0,3}\b",
        r"\b[A-Z]{2,}(?:[- ][A-Z0-9]{2,})*\b",
        r"#[A-Za-z][A-Za-z0-9_]+",
        r"\b(?:Python|JavaScript|TypeScript|React|Streamlit|NetworkX|SQLite|"
        r"machine learning|deep learning|knowledge graph|artificial intelligence|"
        r"neural network|API|database|GitHub|Docker|Kubernetes)\b",
    ]
    for pattern in patterns:
        candidates.extend(re.findall(pattern, text, flags=re.IGNORECASE if "Python" in pattern else 0))
    counts = Counter()
    for item in candidates:
        item = re.sub(r"\s+", " ", item).strip(" .,#")
        if item and item not in STOP and len(item) > 1:
            counts[item] += 1
    return [name for name, _ in counts.most_common(40)]

def extract_relationships(text: str, entities: Iterable[str]) -> list[dict]:
    """Create evidence-backed co-occurrence and simple verb-labelled edges."""
    entity_list = sorted(set(entities), key=len, reverse=True)
    edges: dict[tuple[str, str, str], dict] = {}
    relation_patterns = [
        (r"\buses\b", "USES"), (r"\bbuilt with\b", "BUILT_WITH"),
        (r"\bpart of\b", "PART_OF"), (r"\bworks on\b", "WORKS_ON"),
        (r"\bdepends on\b", "DEPENDS_ON"), (r"\brelated to\b", "RELATED_TO"),
        (r"\bcreated\b", "CREATED"), (r"\bdeveloped\b", "DEVELOPED"),
        (r"\bimplements\b", "IMPLEMENTS"),
    ]
    for sentence in split_sentences(text):
        found = [e for e in entity_list if re.search(r"(?<!\w)" + re.escape(e) + r"(?!\w)", sentence, re.I)]
        if len(found) < 2:
            continue
        label = next((name for pattern, name in relation_patterns if re.search(pattern, sentence, re.I)), "MENTIONED_WITH")
        for i, left in enumerate(found[:8]):
            for right in found[i + 1:8]:
                a, b = sorted((left, right), key=str.casefold)
                key = (a, b, label)
                if key not in edges:
                    edges[key] = {"source": a, "target": b, "label": label, "evidence": sentence[:500], "count": 0}
                edges[key]["count"] += 1
    return list(edges.values())
