from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class Document:
    id: str
    source: str
    title: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    collected_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_chunk_metadata(self) -> dict[str, Any]:
        base = {
            "source": self.source,
            "title": self.title,
            "doc_id": self.id,
            "collected_at": self.collected_at,
        }
        base.update(self.metadata)
        return base
