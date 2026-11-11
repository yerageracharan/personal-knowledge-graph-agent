"""SQLite persistence for documents, entities and graph edges."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class KnowledgeStore:
    def __init__(self, path: str = "data/knowledge.db"):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS documents(
              id INTEGER PRIMARY KEY, name TEXT UNIQUE, text TEXT NOT NULL, added_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS entities(
              name TEXT PRIMARY KEY, mentions INTEGER DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS relationships(
              id INTEGER PRIMARY KEY, source TEXT NOT NULL, target TEXT NOT NULL,
              label TEXT NOT NULL, evidence TEXT NOT NULL, count INTEGER DEFAULT 1,
              UNIQUE(source,target,label,evidence)
            );
            """
        )
        self.db.commit()

    @staticmethod
    def _validate_document(name: str, text: str) -> tuple[str, str]:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Document name must be a non-empty string.")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Document text must be a non-empty string.")
        return name.strip(), text

    @staticmethod
    def _validate_entities(entities: list[str]) -> list[str]:
        if not isinstance(entities, list):
            raise TypeError("entities must be a list of strings.")
        cleaned: list[str] = []
        for index, value in enumerate(entities):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Entity at index {index} must be a non-empty string.")
            value = value.strip()
            if value not in cleaned:
                cleaned.append(value)
        return cleaned

    @staticmethod
    def _validate_relationships(
        relationships: list[dict[str, Any]], entities: list[str], text: str
    ) -> list[dict[str, Any]]:
        if not isinstance(relationships, list):
            raise TypeError("relationships must be a list of relationship objects.")
        entity_set = set(entities)
        cleaned: list[dict[str, Any]] = []
        for index, edge in enumerate(relationships):
            if not isinstance(edge, dict):
                raise ValueError(f"Relationship at index {index} must be an object.")
            fields = {key: edge.get(key) for key in ("source", "target", "label", "evidence")}
            for key, value in fields.items():
                if not isinstance(value, str) or not value.strip():
                    raise ValueError(f"Relationship at index {index} has an empty or invalid {key}.")
                fields[key] = value.strip()
            if fields["source"] not in entity_set or fields["target"] not in entity_set:
                raise ValueError(f"Relationship at index {index} references an entity not in this document.")
            if fields["source"] == fields["target"]:
                raise ValueError(f"Relationship at index {index} cannot connect an entity to itself.")
            if fields["evidence"] not in text:
                raise ValueError(f"Relationship at index {index} has evidence that is not present in the source text.")
            count = edge.get("count", 1)
            if isinstance(count, bool) or not isinstance(count, int) or count < 1:
                raise ValueError(f"Relationship at index {index} count must be a positive integer.")
            fields["count"] = count
            cleaned.append(fields)
        return cleaned

    def add_document(self, name: str, text: str, entities: list[str], relationships: list[dict]) -> bool:
        """Persist one document and its graph atomically.

        Duplicate document names are ignored. Entity names are de-duplicated
        within a document so repeated extraction mentions do not inflate the
        cross-document mention count.
        """
        name, text = self._validate_document(name, text)
        entities = self._validate_entities(entities)
        relationships = self._validate_relationships(relationships, entities, text)

        with self.db:
            cur = self.db.execute(
                "INSERT OR IGNORE INTO documents(name,text) VALUES(?,?)",
                (name, text),
            )
            if cur.rowcount == 0:
                return False
            for entity in entities:
                self.db.execute(
                    """INSERT INTO entities(name,mentions) VALUES(?,1)
                    ON CONFLICT(name) DO UPDATE SET mentions=mentions+1""",
                    (entity,),
                )
            for edge in relationships:
                self.db.execute(
                    """INSERT INTO relationships(source,target,label,evidence,count)
                    VALUES(?,?,?,?,?) ON CONFLICT(source,target,label,evidence)
                    DO UPDATE SET count=count+excluded.count""",
                    (edge["source"], edge["target"], edge["label"], edge["evidence"], edge["count"]),
                )
        return True

    def documents(self):
        return self.db.execute("SELECT id,name,added_at FROM documents ORDER BY id DESC").fetchall()

    def all_entities(self):
        return self.db.execute("SELECT name,mentions FROM entities ORDER BY mentions DESC,name").fetchall()

    def all_relationships(self):
        return self.db.execute("SELECT source,target,label,evidence,count FROM relationships ORDER BY count DESC").fetchall()

    def get_document_texts(self):
        return self.db.execute("SELECT name,text FROM documents").fetchall()

    def stats(self) -> dict[str, int]:
        return {
            "documents": self.db.execute("SELECT COUNT(*) FROM documents").fetchone()[0],
            "entities": self.db.execute("SELECT COUNT(*) FROM entities").fetchone()[0],
            "relationships": self.db.execute("SELECT COUNT(*) FROM relationships").fetchone()[0],
        }

    def close(self) -> None:
        """Close the SQLite connection when the service lifetime ends."""
        self.db.close()
