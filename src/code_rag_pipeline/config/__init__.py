"""Configuration management and settings initialization."""

from code_rag_pipeline.config.settings import setup_llama_settings, DEFAULT_OLLAMA_HOST

__all__ = [
    "DEFAULT_OLLAMA_HOST",
    "setup_llama_settings",
]
