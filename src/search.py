"""Local TF-IDF retrieval with source-grounded answer snippets."""
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def retrieve(query: str, documents: list, limit: int = 5) -> list[dict]:
    chunks = []
    for row in documents:
        name, text = row["name"], row["text"]
        for part in re.split(r"(?<=[.!?])\s+|\n+", text):
            if len(part.strip()) >= 25:
                chunks.append({"source": name, "text": part.strip()})
    if not chunks or not query.strip():
        return []
    corpus = [c["text"] for c in chunks]
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    try:
        matrix = vectorizer.fit_transform(corpus + [query])
    except ValueError:
        return []
    scores = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
    ranked = sorted(zip(scores, chunks), key=lambda item: item[0], reverse=True)
    return [{"score": float(score), **chunk} for score, chunk in ranked[:limit] if score > 0]
