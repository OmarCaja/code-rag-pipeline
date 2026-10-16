import logging

from llama_index.core import Settings
from llama_index.embeddings.openai_like import OpenAILikeEmbedding
from llama_index.llms.openai_like import OpenAILike

from code_rag_pipeline.config import CONTEXT_WINDOW, EMBED_MODEL, LLM_API_BASE, LLM_MODEL, QUERY_INSTRUCTION

logger = logging.getLogger(__name__)


class _InstructedEmbedding(OpenAILikeEmbedding):
    """Prefixes queries with the retrieval instruction Qwen3-Embedding expects; documents are embedded as-is."""

    def _get_query_embedding(self, query: str) -> list[float]:
        return super()._get_query_embedding(QUERY_INSTRUCTION + query)

    async def _aget_query_embedding(self, query: str) -> list[float]:
        return await super()._aget_query_embedding(QUERY_INSTRUCTION + query)


def setup_llama_settings(
        llm_model: str = LLM_MODEL,
        embed_model_name: str = EMBED_MODEL,
        api_base: str = LLM_API_BASE,
) -> None:
    logger.info(
        "Initializing LlamaIndex settings with api_base='%s', llm='%s', embed_model='%s'",
        api_base,
        llm_model,
        embed_model_name,
    )

    Settings.llm = OpenAILike(
        model=llm_model,
        api_base=api_base,
        api_key="lm-studio",
        context_window=CONTEXT_WINDOW,
        is_chat_model=True,
        is_function_calling_model=True,
        timeout=120.0,
    )
    Settings.embed_model = _InstructedEmbedding(
        model_name=embed_model_name,
        api_base=api_base,
        api_key="lm-studio",
    )

    logger.info("LlamaIndex global settings successfully updated.")
