from __future__ import annotations

from bug_investigator.models import Document


def merge_documents(existing: list[Document], new: list[Document]) -> list[Document]:
    seen = {doc.id for doc in existing}
    merged = list(existing)
    for doc in new:
        if doc.id not in seen:
            merged.append(doc)
            seen.add(doc.id)
    return merged
