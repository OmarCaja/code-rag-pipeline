"""Configuration management and settings initialization."""

from .config import DATA_DIR, EMBED_MODEL, EXCLUDE_PATHS, LLM_MODEL, OLLAMA_HOST, SUPPORTED_EXTENSIONS
from .lancedb_settings import INDEX_DIR, LANCEDB_URI
from .logging import setup_logging
from .ollama_settings import setup_llama_settings

__all__ = [
    "DATA_DIR",
    "EMBED_MODEL",
    "EXCLUDE_PATHS",
    "INDEX_DIR",
    "LANCEDB_URI",
    "LLM_MODEL",
    "OLLAMA_HOST",
    "SUPPORTED_EXTENSIONS",
    "setup_logging",
    "setup_llama_settings",
]
