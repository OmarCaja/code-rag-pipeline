from collections import defaultdict
from collections.abc import Sequence
from pathlib import Path

from llama_index.core.schema import Document


def group_documents_by_extension(
        documents: Sequence[Document],
) -> dict[str, list[Document]]:
    docs_by_ext: dict[str, list[Document]] = defaultdict(list)

    for doc in documents:
        raw_path = doc.metadata.get("file_path", "")
        ext = Path(str(raw_path)).suffix.lower()
        docs_by_ext[ext].append(doc)

    return docs_by_ext
