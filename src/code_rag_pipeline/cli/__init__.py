"""CLI module for code-rag-pipeline."""

from .app import app
from .chat_cmd import do_chat
from .index_cmd import do_index

__all__ = ["app", "do_chat", "do_index"]
