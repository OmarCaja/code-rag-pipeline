import logging
from pathlib import Path

from code_rag_pipeline.config import setup_llama_settings, DEFAULT_OLLAMA_HOST
from code_rag_pipeline.core import load_documents
from code_rag_pipeline.utils import setup_logging

setup_logging()

logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Starting Ollama service connectivity check...")

    try:
        test_llm, test_embed = setup_llama_settings()

        logger.info("Testing LLM completion endpoint...")
        response = test_llm.complete("Write a Python palindrome check function.")

        logger.info("LLM Completion successful.")
        logger.debug("LLM Response Payload:\n%s", response.text.strip())

        logger.info("Testing Embedding generation endpoint...")
        embedding_vector = test_embed.get_text_embedding("def hello(): pass")

        logger.info(
            "Embedding generated successfully (Dimensions: %d).",
            len(embedding_vector),
        )

    except Exception as error:
        logger.exception(
            "Failed to communicate with Ollama service at host '%s'.",
            DEFAULT_OLLAMA_HOST,
            error
        )

    logger.info("Loading documents from ./src folder...")

    project_src_dir = Path(__file__).parent.resolve()  # Points to ./src
    load_documents(project_src_dir)


if __name__ == "__main__":
    main()
