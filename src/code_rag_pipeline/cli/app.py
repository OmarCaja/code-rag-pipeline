import logging
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from code_rag_pipeline.config import setup_llama_settings
from code_rag_pipeline.core import CodeParserOrchestrator, load_documents
from code_rag_pipeline.storage import index_nodes, load_index
from code_rag_pipeline.utils import setup_logging

app = typer.Typer(
    name="code-rag",
    help="Local RAG system to index and query codebases.",
    add_completion=False,
    no_args_is_help=True,
)

console = Console()
logger = logging.getLogger(__name__)


@app.command("index")
def index_project(
        name: Annotated[str, typer.Argument(help="The unique name for this project.")],
        path: Annotated[Path, typer.Argument(help="The path to the project directory.")],
) -> None:
    """
    Reads a project directory and parses the code into semantic chunks (BaseNodes).
    """
    setup_logging()

    console.print(f"\n[bold cyan]Starting pipeline for project:[/bold cyan] {name}")
    console.print(f"[cyan]Target path:[/cyan] {path.resolve()}\n")

    try:

        # 1. Load Documents
        console.print("📁 Loading documents...")
        documents = load_documents(path)
        console.print(f"✅ Loaded [bold]{len(documents)}[/bold] documents.\n")

        # 2. Parse and Split into Nodes
        console.print("⚙️ Parsing code and splitting into nodes...")
        orchestrator = CodeParserOrchestrator()
        nodes = orchestrator.split_documents(documents)
        console.print(f"✅ Generated [bold]{len(nodes)}[/bold] semantic nodes.\n")

        # 3. Embed Nodes and Store in LanceDB
        console.print("🧠 Embedding nodes and storing in LanceDB...")
        setup_llama_settings()
        index_nodes(nodes, name)
        console.print("✅ Nodes embedded and stored in LanceDB.\n")

        console.print("[bold green]Pipeline executed successfully![/bold green]")

    except NotADirectoryError as err:
        console.print(f"[bold red]Directory Error:[/bold red] {err}")
        raise typer.Exit(code=1)
    except Exception as err:
        logger.exception("An unexpected error occurred during processing.")
        console.print(f"[bold red]Processing failed:[/bold red] {err}")
        raise typer.Exit(code=1)


@app.command("query")
def query_project(
        name: Annotated[str, typer.Argument(help="The indexed project name to query.")],
        question: Annotated[str, typer.Argument(help="The question to ask about the code.")],
) -> None:
    """
    Asks a question about an indexed project, answering from its code.
    """
    setup_logging()
    setup_llama_settings()

    console.print(f"\n[bold cyan]Querying project:[/bold cyan] {name}")
    console.print(f"[cyan]Question:[/cyan] {question}\n")

    try:
        index = load_index(name)
        query_engine = index.as_query_engine()
        response = query_engine.query(question)
        console.print(f"[bold green]Answer:[/bold green]\n{response}\n")
    except FileNotFoundError as err:
        console.print(f"[bold red]Index Error:[/bold red] {err}")
        raise typer.Exit(code=1)
    except Exception as err:
        logger.exception("An unexpected error occurred during querying.")
        console.print(f"[bold red]Query failed:[/bold red] {err}")
        raise typer.Exit(code=1)


@app.command("list")
def list_projects() -> None:
    """
    List all indexed projects in the system.
    """
    console.print("[yellow]Feature coming soon: Listing indexed projects...[/yellow]")


if __name__ == "__main__":
    app()
