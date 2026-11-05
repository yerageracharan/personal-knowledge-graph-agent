"""SQLite persistence for documents, entities and graph edges."""
import sqlite3
from pathlib import Path
from typing import Any

class KnowledgeStore:
    def __init__(self, path: str = "data/knowledge.db"):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
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
        """)
        self.db.commit()

    def add_document(self, name: str, text: str, entities: list[str], relationships: list[dict]) -> bool:
        cur = self.db.execute("INSERT OR IGNORE INTO documents(name,text) VALUES(?,?)", (name, text))
        if cur.rowcount == 0:
            return False
        for entity in entities:
            self.db.execute("""INSERT INTO entities(name,mentions) VALUES(?,1)
                ON CONFLICT(name) DO UPDATE SET mentions=mentions+1""", (entity,))
        for edge in relationships:
            self.db.execute("""INSERT INTO relationships(source,target,label,evidence,count)
                VALUES(?,?,?,?,?) ON CONFLICT(source,target,label,evidence)
                DO UPDATE SET count=count+1""",
                (edge["source"], edge["target"], edge["label"], edge["evidence"], edge.get("count", 1)))
        self.db.commit()
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
