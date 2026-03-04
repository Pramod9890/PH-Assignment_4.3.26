from typing import Dict


class DocumentStore:
    def __init__(self):
        self._store: Dict[str, str] = {}

    def save(self, document_id: str, text: str) -> None:
        self._store[document_id] = text

    def get(self, document_id: str) -> str | None:
        return self._store.get(document_id)


document_store = DocumentStore()