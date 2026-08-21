from collections import defaultdict
from collections.abc import Sequence
from pathlib import Path

from llama_index.core.schema import Document


def group_documents_by_extension(
        documents: Sequence[Document],
) -> dict[str, list[Document]]:
    """Groups a sequence of LlamaIndex Document instances by their lowercased file extension.

    Args:
        documents: A sequence (list or tuple) of Document objects.

    Returns:
        A dictionary mapping file extensions (e.g., '.py', '.astro', '') to
        lists of corresponding Document objects.
    """

    docs_by_ext: dict[str, list[Document]] = defaultdict(list)

    for doc in documents:
        raw_path = doc.metadata.get("file_path", "")
        ext = Path(str(raw_path)).suffix.lower()
        docs_by_ext[ext].append(doc)

    return docs_by_ext
