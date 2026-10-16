from .config import CONTEXT_WINDOW, DATA_DIR, EMBED_MODEL, EXCLUDE_PATHS, LANCEDB_URI, LLM_API_BASE, LLM_MODEL, MEMORY_LIMIT, QUERY_INSTRUCTION, SIMILARITY_TOP_K, SUPPORTED_EXTENSIONS, SYSTEM_PROMPT, VERSION
from .logging import setup_logging
from .llm_settings import setup_llama_settings

__all__ = [
    "CONTEXT_WINDOW",
    "DATA_DIR",
    "EMBED_MODEL",
    "EXCLUDE_PATHS",
    "LANCEDB_URI",
    "LLM_API_BASE",
    "LLM_MODEL",
    "MEMORY_LIMIT",
    "QUERY_INSTRUCTION",
    "SIMILARITY_TOP_K",
    "SUPPORTED_EXTENSIONS",
    "SYSTEM_PROMPT",
    "VERSION",
    "setup_logging",
    "setup_llama_settings",
]
