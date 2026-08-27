import logging

import questionary
from llama_index.core import VectorStoreIndex
from llama_index.core.chat_engine.types import BaseChatEngine
from llama_index.core.memory import ChatMemoryBuffer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from code_rag_pipeline.config import MEMORY_LIMIT, SIMILARITY_TOP_K, SYSTEM_PROMPT
from code_rag_pipeline.storage import list_projects, load_index
from code_rag_pipeline.utils import count_tokens, show_token_bar

console = Console()
logger = logging.getLogger(__name__)


def _new_chat_engine(index: VectorStoreIndex) -> tuple[ChatMemoryBuffer, BaseChatEngine]:
    memory = ChatMemoryBuffer.from_defaults(token_limit=MEMORY_LIMIT)
    engine = index.as_chat_engine(
        similarity_top_k=SIMILARITY_TOP_K,
        memory=memory,
        system_prompt=SYSTEM_PROMPT,
    )
    return memory, engine


def do_chat() -> None:
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
            index = load_index(project_name)
    except FileNotFoundError as err:
        console.print(f"\n[red]✗ {err}[/red]")
        return

    memory, chat_engine = _new_chat_engine(index)

    console.print()
    console.print(Panel(
        f"[bold]{project_name}[/bold]",
        title="[cyan]Chat Mode[/cyan]",
        subtitle="[dim]'new' = fresh chat | 'exit' = quit[/dim]",
        border_style="green",
    ))
    console.print()

    while True:
        try:
            question = questionary.text("You:").ask()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Bye![/dim]")
            break

        if question is None or question.strip().lower() in ("exit", "chao", "quit", "q"):
            console.print("[dim]Bye![/dim]")
            break

        if question.strip().lower() == "new":
            memory, chat_engine = _new_chat_engine(index)
            console.print(Panel(
                f"[bold]Fresh session[/bold]  [dim]({MEMORY_LIMIT} token memory)[/dim]",
                border_style="green",
                padding=(0, 1),
            ))
            continue

        if not question.strip():
            continue

        with console.status("[cyan]Thinking...[/cyan]", spinner="dots"):
            response = chat_engine.chat(question)

        console.print()
        console.print(Panel(
            Markdown(str(response)),
            title="[green]Assistant[/green]",
            border_style="green",
            padding=(0, 1),
        ))
        messages = memory.get()
        used = sum(count_tokens(str(m)) for m in messages) if messages else 0
        show_token_bar(used, MEMORY_LIMIT, console)
        console.print()
