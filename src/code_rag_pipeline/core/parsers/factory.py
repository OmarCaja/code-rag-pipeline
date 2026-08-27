import logging
from collections.abc import Sequence

from llama_index.core.schema import BaseNode, Document

from code_rag_pipeline.utils import group_documents_by_extension
from .splitters import CodeSplitterParser, TokenSplitterParser

logger = logging.getLogger(__name__)

_python = CodeSplitterParser(language="python")
_js = CodeSplitterParser(language="javascript")
_ts = CodeSplitterParser(language="typescript")
_config = TokenSplitterParser(chunk_size=128, chunk_overlap=20)
_fallback = TokenSplitterParser()

_parser_map: dict[str, CodeSplitterParser | TokenSplitterParser] = {
    ".py": _python,
    ".js": _js,
    ".jsx": _js,
    ".ts": _ts,
    ".tsx": _ts,
    ".json": _config,
    ".toml": _config,
    ".yaml": _config,
}


def split_documents(documents: Sequence[Document]) -> list[BaseNode]:
    logger.info("Splitting %d document(s) into nodes...", len(documents))

    docs_by_ext = group_documents_by_extension(documents)
    nodes: list[BaseNode] = []

    for ext, ext_docs in docs_by_ext.items():
        parser = _parser_map.get(ext)

        if parser is not None:
            try:
                nodes.extend(parser.parse_documents(ext_docs))
                continue
            except (SyntaxError, ValueError, NotImplementedError) as err:
                logger.warning(
                    "%s failed for extension '%s' (%d doc(s)). Falling back. Error: %s",
                    type(parser).__name__,
                    ext,
                    len(ext_docs),
                    err,
                )

        nodes.extend(_fallback.parse_documents(ext_docs))

    logger.info("Generated a total of %d node(s) for indexing.", len(nodes))
    return nodes
