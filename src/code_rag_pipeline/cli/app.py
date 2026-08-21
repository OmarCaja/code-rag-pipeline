import logging
from pathlib import Path
from typing import Annotated

import typer
from llama_index.core import PromptTemplate
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

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

    console.print(Panel.fit("[bold cyan]Code RAG Pipeline[/bold cyan]", subtitle="Local code intelligence"))
    console.print()

    choice = Prompt.ask(
        "What do you want to do?",
        choices=["index", "chat"],
        default="chat",
    )

    if choice == "index":
        _do_index()
    else:
        _do_chat()


def _do_index() -> None:
    console.print(Panel.fit("[bold cyan]Index Project[/bold cyan]"))
    console.print()

    name = Prompt.ask("[cyan]Project name[/cyan]")
    path_str = Prompt.ask("[cyan]Path to project (absolute or relative)[/cyan]")
    path = Path(path_str).expanduser().resolve()

    if not path.is_dir():
        console.print(f"[red]Not a directory: {path}[/red]")
        return

    console.print(f"\n[bold cyan]Starting pipeline for project:[/bold cyan] {name}")
    console.print(f"[cyan]Target path:[/cyan] {path}\n")

    try:
        console.print("Loading documents...")
        documents = load_documents(path)
        console.print(f"Loaded [bold]{len(documents)}[/bold] documents.\n")

        console.print("Parsing code and splitting into nodes...")
        orchestrator = CodeParserOrchestrator()
        nodes = orchestrator.split_documents(documents)
        console.print(f"Generated [bold]{len(nodes)}[/bold] semantic nodes.\n")

        console.print("Embedding nodes and storing in LanceDB...")
        setup_llama_settings()
        index_nodes(nodes, name)
        console.print("Nodes embedded and stored in LanceDB.\n")

        console.print("[bold green]Pipeline executed successfully![/bold green]")

    except Exception as err:
        logger.exception("An unexpected error occurred during processing.")
        console.print(f"[bold red]Processing failed:[/bold red] {err}")


def _do_chat() -> None:
    console.print(Panel.fit("[bold cyan]Chat with Project[/bold cyan]"))
    console.print()

    projects = list_projects()

    if not projects:
        console.print("[yellow]No projects indexed yet.[/yellow]")
        console.print("[dim]Run 'code-rag index' to index a project first.[/dim]")
        return

    table = Table(show_header=False, show_lines=False, padding=(0, 2))
    table.add_column("NUM", style="dim")
    table.add_column("PROJECT", style="cyan bold")
    for i, p in enumerate(projects, 1):
        table.add_row(str(i), p)
    console.print(table)
    console.print()

    selection = Prompt.ask(
        "[cyan]Select project (number or name)[/cyan]",
        choices=[str(i) for i in range(1, len(projects) + 1)] + projects,
        default="1",
    )

    if selection.isdigit():
        idx = int(selection) - 1
        if idx < 0 or idx >= len(projects):
            console.print("[red]Invalid selection.[/red]")
            return
        project_name = projects[idx]
    else:
        project_name = selection

    try:
        setup_llama_settings()
        index = load_index(project_name)
    except FileNotFoundError as err:
        console.print(f"[red]{err}[/red]")
        return

    query_engine = index.as_query_engine(
        similarity_top_k=5,
        text_qa_template=PromptTemplate(SYSTEM_PROMPT),
    )

    console.print(f"\n[bold green]Chatting with project:[/bold green] {project_name}")
    console.print("[dim]Type 'exit' or 'quit' to leave.[/dim]\n")

    while True:
        try:
            question = Prompt.ask("[bold cyan]You[/bold cyan]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Bye![/dim]")
            break

        if question.strip().lower() in ("exit", "quit", "q"):
            console.print("[dim]Bye![/dim]")
            break

        if not question.strip():
            continue

        with console.status("[bold cyan]Thinking...[/bold cyan]", spinner="dots"):
            response = query_engine.query(question)
        console.print(f"\n[bold green]Assistant:[/bold green] {response}\n")


if __name__ == "__main__":
    app()
