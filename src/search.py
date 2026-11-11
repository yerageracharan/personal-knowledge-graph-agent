"""Local TF-IDF retrieval with source-grounded answer snippets."""
from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

MAX_RESULTS = 50
MIN_CHUNK_CHARS = 25


def retrieve(query: str, documents: Sequence[Mapping[str, Any]], limit: int = 5) -> list[dict]:
    """Return the highest-scoring source snippets for a query.

    The result limit is deliberately bounded so callers cannot accidentally ask
    the local UI/MCP service to materialise an unbounded result set.
    """
    if not isinstance(query, str):
        raise TypeError("query must be a string")
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise TypeError("limit must be an integer")
    if not 1 <= limit <= MAX_RESULTS:
        raise ValueError(f"limit must be between 1 and {MAX_RESULTS}")
    if not isinstance(documents, Sequence) or isinstance(documents, (str, bytes)):
        raise TypeError("documents must be a sequence of document records")
    if not query.strip() or not documents:
        return []

    chunks: list[dict[str, str]] = []
    for index, row in enumerate(documents):
        if isinstance(row, Mapping):
            record = row
        elif callable(getattr(row, "keys", None)) and hasattr(row, "__getitem__"):
            # sqlite3.Row supports keyed access and keys(), but is not registered
            # as collections.abc.Mapping.
            record = {key: row[key] for key in row.keys()}
        else:
            raise TypeError(f"documents[{index}] must be a mapping with name and text fields")
        name, text = record.get("name"), record.get("text")
        if not isinstance(name, str) or not isinstance(text, str):
            raise ValueError(f"documents[{index}] must contain string 'name' and 'text' fields")
        for part in re.split(r"(?<=[.!?])\\s+|\\n+", text):
            snippet = part.strip()
            if len(snippet) >= MIN_CHUNK_CHARS:
                chunks.append({"source": name, "text": snippet})

    if not chunks:
        return []

    corpus = [chunk["text"] for chunk in chunks]
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    try:
        matrix = vectorizer.fit_transform(corpus + [query])
    except ValueError:
        # Empty vocabularies (for example, punctuation-only text) are not errors.
        return []

    scores = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
    ranked = sorted(zip(scores, chunks), key=lambda item: item[0], reverse=True)
    return [
        {"score": float(score), **chunk}
        for score, chunk in ranked[:limit]
        if score > 0
    ]
