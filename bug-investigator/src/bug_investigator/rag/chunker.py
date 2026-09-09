from __future__ import annotations

import re
from typing import Iterable

from bug_investigator.models import Document


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> list[str]:
    text = re.sub(r"\n{3,}", "\n\n", text.strip())
    if len(text) <= chunk_size:
        return [text]
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            split_at = text.rfind("\n", start, end)
            if split_at > start + chunk_size // 2:
                end = split_at
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def chunk_documents(
    documents: Iterable[Document],
    chunk_size: int,
    overlap: int,
) -> list[tuple[str, str, dict]]:
    results: list[tuple[str, str, dict]] = []
    for doc in documents:
        parts = chunk_text(doc.content, chunk_size, overlap)
        for idx, part in enumerate(parts):
            chunk_id = f"{doc.id}::chunk-{idx}"
            meta = doc.to_chunk_metadata()
            meta["chunk_index"] = idx
            meta["chunk_total"] = len(parts)
            results.append((chunk_id, part, meta))
    return results
