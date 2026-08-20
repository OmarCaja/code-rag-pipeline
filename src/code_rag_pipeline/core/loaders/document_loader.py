import logging
from pathlib import Path

from llama_index.core import SimpleDirectoryReader
from llama_index.core.schema import Document

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS: list[str] = [
    ".py",
    ".js",
    ".ts",
    ".less",
    ".css",
    ".json",
    ".md",
]


def load_documents(target_dir: Path | str) -> list[Document]:
    """Loads source code documents from the target directory matching allowed extensions.

    Args:
        target_dir: Directory path as a string or Path instance.

    Returns:
        List of loaded LlamaIndex Document instances.

    Raises:
        NotADirectoryError: If the target path does not exist or is not a directory.
    """
    path = Path(target_dir).resolve()

    if not path.is_dir():
        raise NotADirectoryError(f"Target directory does not exist or is not a directory: {path}")

    logger.info("Loading documents from directory: %s", path)

    reader = SimpleDirectoryReader(
        input_dir=path,
        required_exts=SUPPORTED_EXTENSIONS,
        recursive=True,
        exclude_hidden=True,  # Ignores .git, .venv, etc.
    )

    documents = reader.load_data()
    loaded_files = [doc.metadata.get("file_path", "Unknown Path") for doc in documents]
    logger.info("Successfully loaded %d document(s).", len(documents))
    logger.debug("Loaded files:\n%s", "\n".join(f" - {file}" for file in loaded_files))
    return documents
