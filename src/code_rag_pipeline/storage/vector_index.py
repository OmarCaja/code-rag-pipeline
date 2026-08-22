import logging
from collections.abc import Sequence

import lancedb
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.schema import BaseNode
from llama_index.vector_stores.lancedb import LanceDBVectorStore

from code_rag_pipeline.config import LANCEDB_URI

logger = logging.getLogger(__name__)


def index_nodes(
        nodes: Sequence[BaseNode],
        project_name: str,
) -> VectorStoreIndex:
    """Embeds nodes via the global `Settings.embed_model` and stores them in LanceDB.

    One LanceDB table per project. LanceDB stores vectors + text, no separate
    docstore needed.

    Args:
        nodes: Nodes produced by the document parsers/splitters.
        project_name: Unique name for the project; used as the table name.

    Returns:
        The built VectorStoreIndex, ready for querying.
    """
    vector_store = LanceDBVectorStore(uri=str(LANCEDB_URI), table_name=project_name, mode="overwrite")
    index = VectorStoreIndex(nodes=nodes, storage_context=StorageContext.from_defaults(vector_store=vector_store))

    logger.info("Stored %d node(s) in LanceDB table '%s' (%s).", len(nodes), project_name, LANCEDB_URI)
    return index


def load_index(
        project_name: str,
) -> VectorStoreIndex:
    """Reloads a previously indexed project for querying.

    Args:
        project_name: Indexed project to load; used as the LanceDB table name.
    """
    if project_name not in list_projects():
        raise FileNotFoundError(
            f"No index found for project '{project_name}'. Run 'code-rag index {project_name} <path>' first.")

    vector_store = LanceDBVectorStore(uri=str(LANCEDB_URI), table_name=project_name)
    return VectorStoreIndex.from_vector_store(vector_store)


def list_projects() -> list[str]:
    """Returns names of all indexed projects (LanceDB tables)."""
    db = lancedb.connect(str(LANCEDB_URI))
    return sorted(table_name for table_name in db.table_names() if not table_name.startswith("_"))
