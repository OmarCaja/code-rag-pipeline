import logging
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from code_rag_pipeline.core import CodeParserOrchestrator, load_documents
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

    # Temporarily silence verbose logs so the output stays clean
    root_logger = logging.getLogger()
    previous_level = root_logger.level
    root_logger.setLevel(logging.WARNING)

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

        console.print("[bold green]Pipeline executed successfully![/bold green] Nodes are ready for embedding.")

    except NotADirectoryError as err:
        console.print(f"[bold red]Directory Error:[/bold red] {err}")
        raise typer.Exit(code=1)
    except Exception as err:
        logger.exception("An unexpected error occurred during processing.")
        console.print(f"[bold red]Processing failed:[/bold red] {err}")
        raise typer.Exit(code=1)

    finally:
        root_logger.setLevel(previous_level)


@app.command("list")
def list_projects() -> None:
    """
    List all indexed projects in the system.
    """
    console.print("[yellow]Feature coming soon: Listing indexed projects...[/yellow]")


if __name__ == "__main__":
    app()
