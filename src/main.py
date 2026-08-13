import logging

from config.settings import setup_llama_settings, DEFAULT_OLLAMA_HOST
from utils.logger import setup_logging

setup_logging()

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting Ollama service connectivity check...")

    test_llm, test_embed = setup_llama_settings()

    try:
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
            "Failed to communicate with Ollama service at '%s'. Context: %s",
            DEFAULT_OLLAMA_HOST,
            error,
        )
