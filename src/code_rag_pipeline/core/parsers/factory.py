import logging
from typing import Sequence

from llama_index.core.schema import BaseNode, Document

from code_rag_pipeline.utils import group_documents_by_extension
from .base import BaseCodeParser
from .fallback_parser import FallbackParser
from .python_parser import PythonCodeParser

logger = logging.getLogger(__name__)


class CodeParserOrchestrator:
    """Orchestrates document splitting by routing extensions to specialized parsers."""

    def __init__(self) -> None:
        self._python_parser = PythonCodeParser()
        self._fallback_parser = FallbackParser()

        # Strategy Map: Map file extensions to their specialized parsers
        self._parser_map: dict[str, BaseCodeParser] = {
            ".py": self._python_parser,
            # Easily extend with new parsers in the future:
            # ".astro": AstroCodeParser(),
            # ".ts": TypescriptParser(),
        }

    def split_documents(self, documents: Sequence[Document]) -> list[BaseNode]:
        """Batches documents by file extension and parses them into nodes."""
        logger.info("Splitting %d document(s) into nodes...", len(documents))

        docs_by_ext = group_documents_by_extension(documents)

        nodes: list[BaseNode] = []

        for ext, ext_docs in docs_by_ext.items():
            parser = self._parser_map.get(ext)

            if parser is not None:
                try:
                    split_nodes = parser.parse_documents(ext_docs)
                    nodes.extend(split_nodes)
                    continue
                except Exception as err:
                    logger.warning(
                        "%s failed for extension '%s' (%d doc(s)). Falling back to FallbackParser. Error: %s",
                        parser.__class__.__name__,
                        ext,
                        len(ext_docs),
                        err,
                    )

            # Fallback for unregistered extensions or failed AST processing
            fallback_nodes = self._fallback_parser.parse_documents(ext_docs)
            nodes.extend(fallback_nodes)

        logger.info("Generated a total of %d node(s) for indexing.", len(nodes))
        return nodes
