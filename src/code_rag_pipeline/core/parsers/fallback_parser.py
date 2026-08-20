import logging
from typing import Sequence

from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.schema import BaseNode, Document

from code_rag_pipeline.core.parsers import BaseCodeParser

logger = logging.getLogger(__name__)


class FallbackParser(BaseCodeParser):
    """Handles token-based text splitting for non-code or unsupported files."""

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50) -> None:
        self._splitter = TokenTextSplitter.from_defaults(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def parse_documents(self, documents: Sequence[Document]) -> list[BaseNode]:
        logger.debug("Parsing %d document(s) via TokenTextSplitter...", len(documents))
        return self._splitter.get_nodes_from_documents(documents)
