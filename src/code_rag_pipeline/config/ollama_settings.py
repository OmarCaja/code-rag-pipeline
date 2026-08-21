import logging
from typing import cast

from llama_index.core import Settings
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.llms import LLM
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama

from code_rag_pipeline.config import EMBED_MODEL, LLM_MODEL, OLLAMA_HOST

logger = logging.getLogger(__name__)


def setup_llama_settings(
        llm_model: str = LLM_MODEL,
        embed_model_name: str = EMBED_MODEL,
        ollama_host: str = OLLAMA_HOST,
        query_instruction: str = "search_query: ",
) -> tuple[LLM, BaseEmbedding]:
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

    embed_model = cast(BaseEmbedding, OllamaEmbedding(
        model_name=embed_model_name,
        base_url=ollama_host,
        query_instruction=query_instruction,
    ))

    Settings.llm = llm
    Settings.embed_model = embed_model

    logger.info("LlamaIndex global settings successfully updated.")
    return llm, embed_model
