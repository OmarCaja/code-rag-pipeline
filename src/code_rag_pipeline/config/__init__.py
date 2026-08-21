"""Configuration management and settings initialization."""

from code_rag_pipeline.config.logging import setup_logging
from code_rag_pipeline.config.settings import setup_llama_settings, DEFAULT_OLLAMA_HOST

__all__ = [
    "DEFAULT_OLLAMA_HOST",
    "setup_logging",
    "setup_llama_settings",
]
