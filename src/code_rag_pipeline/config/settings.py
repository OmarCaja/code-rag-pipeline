import logging
import os
from typing import Tuple

from llama_index.core import Settings
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.llms import LLM
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama

logger = logging.getLogger(__name__)

DEFAULT_OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen2.5-coder:7b")
DEFAULT_EMBED_MODEL: str = os.getenv("EMBED_MODEL", "nomic-embed-text")


def setup_llama_settings(
        llm_model: str = DEFAULT_LLM_MODEL,
        embed_model_name: str = DEFAULT_EMBED_MODEL,
        ollama_host: str = DEFAULT_OLLAMA_HOST,
        query_instruction: str = "search_query: ",
) -> Tuple[LLM, BaseEmbedding]:
    """Configures LlamaIndex global settings to connect with local Ollama services."""

    logger.info(
        "Initializing LlamaIndex settings with host='%s', llm='%s', embed_model='%s'",
        ollama_host,
        llm_model,
        embed_model_name,
    )

    llm: LLM = Ollama(
        model=llm_model,
        base_url=ollama_host,
        request_timeout=120.0,
    )

    embed_model: BaseEmbedding = OllamaEmbedding(
        model_name=embed_model_name,
        base_url=ollama_host,
        query_instruction=query_instruction,
    )

    Settings.llm = llm
    Settings.embed_model = embed_model

    logger.info("LlamaIndex global settings successfully updated.")
    return llm, embed_model
