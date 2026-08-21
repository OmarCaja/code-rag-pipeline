import logging
from collections.abc import Sequence

from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.schema import BaseNode, Document

from .base import BaseCodeParser

logger = logging.getLogger(__name__)


class ConfigParser(BaseCodeParser):
    """Handles token-based splitting for config/data files (smaller chunks)."""

    def __init__(self, chunk_size: int = 128, chunk_overlap: int = 20) -> None:
        self._splitter = TokenTextSplitter.from_defaults(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def parse_documents(self, documents: Sequence[Document]) -> list[BaseNode]:
        logger.debug("Parsing %d config document(s) via TokenTextSplitter...", len(documents))
        return self._splitter.get_nodes_from_documents(documents)
