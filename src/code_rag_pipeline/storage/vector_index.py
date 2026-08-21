import logging
import os
from pathlib import Path
from typing import Sequence, cast

from llama_index.core import StorageContext, VectorStoreIndex, load_index_from_storage
from llama_index.core.schema import BaseNode
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.storage.index_store import SimpleIndexStore
from llama_index.vector_stores.lancedb import LanceDBVectorStore

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = Path(os.getenv("DATA_DIR", PROJECT_ROOT / "data"))


def index_nodes(
        nodes: Sequence[BaseNode],
        project_name: str,
        lancedb_uri: Path | str | None = None,
        persist_dir: Path | str | None = None,
) -> VectorStoreIndex:
    """Embeds nodes via the global `Settings.embed_model` and stores them in LanceDB.

    Uses one shared LanceDB directory with a table per project. The docstore/index
    is persisted alongside so the index can be reloaded later for queries.

    Args:
        nodes: Nodes produced by the document parsers/splitters.
        project_name: Unique name for the project; used as the table name.
        lancedb_uri: Directory holding the LanceDB stores. Defaults to `data/lancedb`.
        persist_dir: Directory for index/docstore metadata. Defaults to `data/index/{project_name}`.

    Returns:
        The built VectorStoreIndex, ready for querying.
    """
    uri = Path(lancedb_uri) if lancedb_uri else DATA_DIR / "lancedb"
    persist = Path(persist_dir) if persist_dir else DATA_DIR / "index" / project_name

    # mode="overwrite" nukes the table on each run -> reindex is idempotent
    vector_store = LanceDBVectorStore(uri=str(uri), table_name=project_name, mode="overwrite")
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex(nodes=nodes, storage_context=storage_context)
    index.storage_context.persist(persist_dir=str(persist))

    logger.info("Stored %d node(s) in LanceDB table '%s' (%s).", len(nodes), project_name, uri)
    return index


def load_index(
        project_name: str,
        lancedb_uri: Path | str | None = None,
        persist_dir: Path | str | None = None,
) -> VectorStoreIndex:
    """Reloads a previously indexed project for querying.

    LanceDB lives outside the persist dir, so the vector store must be re-attached
    explicitly; docstore/index metadata come from the persisted JSON.

    Args:
        project_name: Indexed project to load; used as the LanceDB table name.
        lancedb_uri: Directory holding the LanceDB stores. Defaults to `data/lancedb`.
        persist_dir: Directory with the persisted index metadata. Defaults to `data/index/{project_name}`.
    """
    uri = Path(lancedb_uri) if lancedb_uri else DATA_DIR / "lancedb"
    persist = Path(persist_dir) if persist_dir else DATA_DIR / "index" / project_name

    if not (persist / "index_store.json").exists():
        raise FileNotFoundError(
            f"No index found for project '{project_name}'. Run 'code-rag index {project_name} <path>' first.")

    vector_store = LanceDBVectorStore(uri=str(uri), table_name=project_name)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    storage_context.docstore = SimpleDocumentStore.from_persist_dir(str(persist))
    storage_context.index_store = SimpleIndexStore.from_persist_dir(str(persist))

    logger.info("Loaded index for project '%s' (%s).", project_name, uri)
    return cast(VectorStoreIndex, load_index_from_storage(storage_context))
