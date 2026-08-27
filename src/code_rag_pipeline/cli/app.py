import logging
from typing import Annotated

import questionary
import typer
from rich.console import Console

from code_rag_pipeline.config import VERSION, setup_llama_settings, setup_logging
from .chat_cmd import do_chat
from .index_cmd import do_index

app = typer.Typer(
    name="code-rag",
    help="Local RAG system to index and query codebases.",
    add_completion=False
)

console = Console()


@app.callback(invoke_without_command=True)
def main(
        verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable debug logging.")] = False,
) -> None:
    setup_logging(logging.DEBUG if verbose else logging.WARNING)
    setup_llama_settings()

    console.print(f"[bold cyan]Code RAG Pipeline[/bold cyan] [dim]v{VERSION}[/dim]\n")

    commands = {
        "Chat with a project": do_chat,
        "Index a new project": do_index,
    }

    choice = questionary.select(
        "What do you want to do?",
        choices=list(commands),
    ).ask()

    if choice is not None:
        commands[choice]()


if __name__ == "__main__":
    app()
