import logging
from pathlib import Path

from llama_index.core import SimpleDirectoryReader
from llama_index.core.schema import Document

from code_rag_pipeline.config import EXCLUDE_PATHS, SUPPORTED_EXTENSIONS

logger = logging.getLogger(__name__)


def load_documents(target_dir: Path | str) -> list[Document]:
    path = Path(target_dir).resolve()

    if not path.is_dir():
        raise NotADirectoryError(f"Target directory does not exist or is not a directory: {path}")

    logger.info("Loading documents from directory: %s", path)

    reader = SimpleDirectoryReader(
        input_dir=path,
        required_exts=SUPPORTED_EXTENSIONS,
        recursive=True,
        exclude_hidden=True,
        exclude=EXCLUDE_PATHS,
    )

    documents = reader.load_data()

    loaded_files = [doc.metadata.get("file_path", "Unknown Path") for doc in documents]
    logger.info("Successfully loaded %d document(s).", len(documents))
    logger.debug("Loaded files:\n%s", "\n".join(f" - {file}" for file in loaded_files))
    return documents
