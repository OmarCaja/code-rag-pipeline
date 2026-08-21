"""Configuration management and settings initialization."""

from .config import DATA_DIR, OLLAMA_HOST, LLM_MODEL, EMBED_MODEL
from .lancedb_settings import INDEX_DIR, LANCEDB_URI
from .logging import setup_logging
from .ollama_settings import setup_llama_settings

__all__ = [
    "DATA_DIR",
    "OLLAMA_HOST",
    "LLM_MODEL",
    "EMBED_MODEL",
    "INDEX_DIR",
    "LANCEDB_URI",
    "setup_logging",
    "setup_llama_settings",
]
