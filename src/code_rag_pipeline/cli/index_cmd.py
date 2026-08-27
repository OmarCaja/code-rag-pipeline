import logging

import questionary
from rich.console import Console
from rich.panel import Panel

from code_rag_pipeline.core import split_documents, load_documents
from code_rag_pipeline.storage import index_nodes
from code_rag_pipeline.utils import cleanup_temp, resolve_project_path

console = Console()
logger = logging.getLogger(__name__)


def do_index() -> None:
    console.print()
    path_str = questionary.text("Path or git URL to project:").ask()
    if not path_str:
        return

    try:
        name, path, tmp_dir = resolve_project_path(path_str)
    except Exception as err:
        console.print(f"\n[red]✗ {err}[/red]")
        return

    try:
        console.print()
        console.print(Panel(
            f"[bold]{name}[/bold]\n[dim]{path}[/dim]",
            title="[cyan]Indexing Project[/cyan]",
            border_style="cyan",
        ))
        console.print()

        with console.status("[cyan]Loading documents...[/cyan]", spinner="dots"):
            documents = load_documents(path)
        for doc in documents:
            doc.metadata["file_path"] = doc.metadata.get("file_path", "").removeprefix(f"{path}/")
        console.print(f"  [green]✓[/green] Loaded [bold]{len(documents)}[/bold] documents")

        with console.status("[cyan]Parsing and splitting...[/cyan]", spinner="dots"):
            nodes = split_documents(documents)
        console.print(f"  [green]✓[/green] Generated [bold]{len(nodes)}[/bold] nodes")

        with console.status("[cyan]Embedding and storing...[/cyan]", spinner="dots"):
            index_nodes(nodes, name)
        console.print("  [green]✓[/green] Stored in LanceDB")

        console.print()
        console.print(Panel("[bold green]Done![/bold green]", border_style="green"))

    except Exception as err:
        logger.exception("An unexpected error occurred during processing.")
        console.print(f"\n[red]✗ Processing failed:[/red] {err}")
    finally:
        if tmp_dir:
            cleanup_temp(tmp_dir)
            console.print(f"  [dim]✓ Cleaned up temp folder:[/dim] {tmp_dir}")
