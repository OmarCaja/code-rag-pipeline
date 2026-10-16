"""MCP server (stdio) exposing the indexed codebases to agents. stdout carries the protocol; logs go to stderr."""
import logging
from typing import Any

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from code_rag_pipeline.config import SIMILARITY_TOP_K, SYSTEM_PROMPT, setup_llama_settings, setup_logging
from code_rag_pipeline.core import load_documents, split_documents
from code_rag_pipeline import storage
from code_rag_pipeline.utils import cleanup_temp, resolve_project_path

logger = logging.getLogger(__name__)

server = MCPServer(
    name="code-rag",
    log_level="WARNING",
    instructions=(
        "Semantic search over locally indexed codebases. Call list_projects first, then search_code "
        "with a natural-language query to get relevant code chunks with their file paths."
    ),
)


def _load(project: str) -> Any:
    try:
        return storage.load_index(project)
    except FileNotFoundError:
        raise ToolError(f"Unknown project '{project}'. Indexed projects: {storage.list_projects()}") from None


@server.tool()
def list_projects() -> list[str]:
    """List the names of all indexed projects."""
    return storage.list_projects()


@server.tool()
def search_code(project: str, query: str, top_k: int = 8) -> list[dict[str, Any]]:
    """Semantic search in an indexed project. Returns the most relevant code chunks with file path and score.

    Args:
        project: Project name from list_projects.
        query: Natural-language description of what you are looking for.
        top_k: Number of chunks to return (1-50).
    """
    retriever = _load(project).as_retriever(similarity_top_k=max(1, min(top_k, 50)))
    return [
        {
            "file_path": hit.node.metadata.get("file_path", ""),
            "score": round(hit.score or 0.0, 4),
            "content": hit.node.get_content(),
        }
        for hit in retriever.retrieve(query)
    ]


@server.tool()
def ask_codebase(project: str, question: str) -> str:
    """Answer a question about a project using the local LLM over retrieved code (single turn, no memory).

    Args:
        project: Project name from list_projects.
        question: The question to answer.
    """
    engine = _load(project).as_chat_engine(
        chat_mode="context", similarity_top_k=SIMILARITY_TOP_K, system_prompt=SYSTEM_PROMPT
    )
    return str(engine.chat(question))


@server.tool()
def index_project(path_or_url: str) -> str:
    """Index (or re-index) a project from a local directory path or a git URL. Replaces any existing index
    with the same name (the directory/repo name). Large repositories can take several minutes.

    Args:
        path_or_url: Absolute local path or git URL (https://, http://, git@).
    """
    try:
        name, path, tmp_dir = resolve_project_path(path_or_url)
    except Exception as err:
        raise ToolError(str(err)) from err

    try:
        nodes = split_documents(load_documents(path))
        storage.index_nodes(nodes, name)
    except NotADirectoryError as err:
        raise ToolError(str(err)) from err
    finally:
        if tmp_dir:
            cleanup_temp(tmp_dir)

    return f"Indexed project '{name}' ({len(nodes)} chunks)."


def main() -> None:
    setup_logging(logging.WARNING)
    setup_llama_settings()
    server.run("stdio")


if __name__ == "__main__":
    main()
