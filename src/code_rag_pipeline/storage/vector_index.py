import functools
import logging
from collections.abc import Sequence

import lancedb
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.schema import BaseNode
from llama_index.vector_stores.lancedb import LanceDBVectorStore

from code_rag_pipeline.config import LANCEDB_URI

logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=1)
def _get_db():
    return lancedb.connect(str(LANCEDB_URI))


def index_nodes(
        nodes: Sequence[BaseNode],
        project_name: str,
) -> VectorStoreIndex:
    db = _get_db()
    if project_name in db.table_names():
        db.drop_table(project_name)
        logger.info("Dropped existing table '%s'.", project_name)

    vector_store = LanceDBVectorStore(uri=str(LANCEDB_URI), table_name=project_name, mode="overwrite")
    index = VectorStoreIndex(nodes=nodes, storage_context=StorageContext.from_defaults(vector_store=vector_store))

    logger.info("Stored %d node(s) in LanceDB table '%s' (%s).", len(nodes), project_name, LANCEDB_URI)
    return index


def load_index(project_name: str) -> VectorStoreIndex:
    if project_name not in list_projects():
        raise FileNotFoundError(
            f"No index found for project '{project_name}'. Run 'code-rag index {project_name} <path>' first.")

    vector_store = LanceDBVectorStore(uri=str(LANCEDB_URI), table_name=project_name)
    return VectorStoreIndex.from_vector_store(vector_store)


def list_projects() -> list[str]:
    db = _get_db()
    return sorted(name for name in db.table_names() if not name.startswith("_"))
