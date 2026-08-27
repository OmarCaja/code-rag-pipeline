from dataclasses import dataclass
from collections.abc import Sequence

from llama_index.core.node_parser import CodeSplitter, TokenTextSplitter
from llama_index.core.schema import BaseNode, Document


@dataclass
class CodeSplitterParser:
    language: str
    chunk_lines: int = 40
    chunk_lines_overlap: int = 15
    max_chars: int = 1500

    def parse_documents(self, documents: Sequence[Document]) -> list[BaseNode]:
        splitter = CodeSplitter.from_defaults(
            language=self.language,
            chunk_lines=self.chunk_lines,
            chunk_lines_overlap=self.chunk_lines_overlap,
            max_chars=self.max_chars,
        )
        return splitter.get_nodes_from_documents(documents)


@dataclass
class TokenSplitterParser:
    chunk_size: int = 512
    chunk_overlap: int = 50

    def parse_documents(self, documents: Sequence[Document]) -> list[BaseNode]:
        splitter = TokenTextSplitter.from_defaults(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )
        return splitter.get_nodes_from_documents(documents)
