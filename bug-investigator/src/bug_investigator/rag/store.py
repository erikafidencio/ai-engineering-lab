from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings

from bug_investigator.config import AppConfig


class VectorStore:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.persist_dir = config.data_dir / "chroma"
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.collection_name = config.get(
            "indexing", "collection_name", default="shopflow-incidents"
        )
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def reset(self) -> None:
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def upsert(
        self,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]],
    ) -> None:
        batch_size = 100
        for start in range(0, len(ids), batch_size):
            end = start + batch_size
            self.collection.upsert(
                ids=ids[start:end],
                documents=documents[start:end],
                embeddings=embeddings[start:end],
                metadatas=metadatas[start:end],
            )

    def query(
        self,
        query_embedding: list[float],
        n_results: int = 8,
        source_filter: str | None = None,
    ) -> dict[str, Any]:
        where = {"source": source_filter} if source_filter else None
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

    def count(self) -> int:
        return self.collection.count()

    def save_manifest(self, stats: dict[str, Any]) -> Path:
        manifest = {
            "indexed_at": datetime.now(timezone.utc).isoformat(),
            "collection": self.collection_name,
            "chunk_count": self.count(),
            **stats,
        }
        path = self.config.data_dir / "manifest.json"
        path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return path
