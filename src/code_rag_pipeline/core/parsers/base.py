from abc import ABC, abstractmethod
from typing import Sequence
from llama_index.core.schema import BaseNode, Document

class BaseCodeParser(ABC):
    """Abstract interface for all document/code splitting strategies."""

    @abstractmethod
    def parse_documents(self, documents: Sequence[Document]) -> list[BaseNode]:
        """Splits a sequence of documents into semantic nodes."""
        pass