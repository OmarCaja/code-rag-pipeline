import logging
from collections.abc import Sequence

from llama_index.core.node_parser import CodeSplitter
from llama_index.core.schema import BaseNode, Document

from .base import BaseCodeParser

logger = logging.getLogger(__name__)


class PythonCodeParser(BaseCodeParser):
    """Handles AST-based code splitting for Python files."""

    def __init__(self, chunk_lines: int = 40, chunk_lines_overlap: int = 15, max_chars: int = 1500) -> None:
        self._splitter = CodeSplitter.from_defaults(
            language="python",
            chunk_lines=chunk_lines,
            chunk_lines_overlap=chunk_lines_overlap,
            max_chars=max_chars,
        )

    def parse_documents(self, documents: Sequence[Document]) -> list[BaseNode]:
        logger.debug("Parsing %d Python document(s) via CodeSplitter...", len(documents))
        return self._splitter.get_nodes_from_documents(documents)
