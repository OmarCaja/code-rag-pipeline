import tiktoken
from rich.console import Console


def count_tokens(text: str) -> int:
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def show_token_bar(used: int, total: int, console: Console, width: int = 30) -> None:
    """Display a simple token usage bar."""
    filled = int(used / total * width) if total else 0
    bar = "█" * filled + "░" * (width - filled)
    console.print(f"[dim]Tokens: {used}/{total}[/dim] {bar}")
