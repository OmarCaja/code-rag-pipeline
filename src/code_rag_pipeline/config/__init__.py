from .config import DATA_DIR, EMBED_MODEL, EXCLUDE_PATHS, LANCEDB_URI, LLM_MODEL, MEMORY_LIMIT, OLLAMA_HOST, SIMILARITY_TOP_K, SUPPORTED_EXTENSIONS, SYSTEM_PROMPT, VERSION
from .logging import setup_logging
from .ollama_settings import setup_llama_settings

__all__ = [
    "DATA_DIR",
    "EMBED_MODEL",
    "EXCLUDE_PATHS",
    "LANCEDB_URI",
    "LLM_MODEL",
    "MEMORY_LIMIT",
    "OLLAMA_HOST",
    "SIMILARITY_TOP_K",
    "SUPPORTED_EXTENSIONS",
    "SYSTEM_PROMPT",
    "VERSION",
    "setup_logging",
    "setup_llama_settings",
]
