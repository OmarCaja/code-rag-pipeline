import logging
from pathlib import Path
from typing import Annotated

import questionary
import typer
from llama_index.core import PromptTemplate
from rich.console import Console
from rich.panel import Panel

from code_rag_pipeline import __version__
from code_rag_pipeline.config import SYSTEM_PROMPT, setup_llama_settings, setup_logging
from code_rag_pipeline.core import CodeParserOrchestrator, load_documents
from code_rag_pipeline.storage import index_nodes, list_projects, load_index

app = typer.Typer(
    name="code-rag",
    help="Local RAG system to index and query codebases.",
)

console = Console()
logger = logging.getLogger(__name__)


@app.callback(invoke_without_command=True)
def main(
        verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable debug logging.")] = False,
) -> None:
    setup_logging(logging.DEBUG if verbose else logging.WARNING)

    console.print(f"[bold cyan]Code RAG Pipeline[/bold cyan] [dim]v{__version__}[/dim]\n")

    choice = questionary.select(
        "What do you want to do?",
        choices=["Chat with a project", "Index a new project"],
    ).ask()

    if choice is None:
        return

    if choice == "Index a new project":
        _do_index()
    else:
        _do_chat()


def _do_index() -> None:
    console.print()
    path_str = questionary.text("Path to project (absolute or relative):").ask()
    if not path_str:
        return

    path = Path(path_str).expanduser().resolve()

    if not path.is_dir():
        console.print(f"\n[red]✗ Not a directory:[/red] {path}")
        return

    name = path.name

    console.print()
    console.print(Panel(
        f"[bold]{name}[/bold]\n[dim]{path}[/dim]",
        title="[cyan]Indexing Project[/cyan]",
        border_style="cyan",
    ))
    console.print()

    try:
        with console.status("[cyan]Loading documents...[/cyan]", spinner="dots"):
            documents = load_documents(path)
        console.print(f"  [green]✓[/green] Loaded [bold]{len(documents)}[/bold] documents")

        with console.status("[cyan]Parsing and splitting...[/cyan]", spinner="dots"):
            orchestrator = CodeParserOrchestrator()
            nodes = orchestrator.split_documents(documents)
        console.print(f"  [green]✓[/green] Generated [bold]{len(nodes)}[/bold] nodes")

        with console.status("[cyan]Embedding and storing...[/cyan]", spinner="dots"):
            setup_llama_settings()
            index_nodes(nodes, name)
        console.print(f"  [green]✓[/green] Stored in LanceDB")

        console.print()
        console.print(Panel("[bold green]Done![/bold green]", border_style="green"))

    except Exception as err:
        logger.exception("An unexpected error occurred during processing.")
        console.print(f"\n[red]✗ Processing failed:[/red] {err}")


def _do_chat() -> None:
    console.print()

    projects = list_projects()

    if not projects:
        console.print("[yellow]No projects indexed yet.[/yellow]")
        console.print("[dim]  Run 'code-rag' and select 'Index a new project' first.[/dim]")
        return

    project_name = questionary.select(
        "Select a project:",
        choices=projects,
    ).ask()

    if not project_name:
        return

    try:
        with console.status("[cyan]Loading index...[/cyan]", spinner="dots"):
            setup_llama_settings()
            index = load_index(project_name)
    except FileNotFoundError as err:
        console.print(f"\n[red]✗ {err}[/red]")
        return

    query_engine = index.as_query_engine(
        similarity_top_k=5,
        text_qa_template=PromptTemplate(SYSTEM_PROMPT),
    )

    console.print()
    console.print(Panel(
        f"[bold]{project_name}[/bold]",
        title="[cyan]Chat Mode[/cyan]",
        subtitle="[dim]Type 'exit' to leave[/dim]",
        border_style="green",
    ))
    console.print()

    while True:
        try:
            question = questionary.text("You:").ask()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Bye![/dim]")
            break

        if question is None or question.strip().lower() in ("exit", "quit", "q"):
            console.print("[dim]Bye![/dim]")
            break

        if not question.strip():
            continue

        with console.status("[cyan]Thinking...[/cyan]", spinner="dots"):
            response = query_engine.query(question)

        console.print()
        console.print(Panel(
            str(response),
            title="[green]Assistant[/green]",
            border_style="green",
            padding=(0, 1),
        ))
        console.print()


if __name__ == "__main__":
    app()
