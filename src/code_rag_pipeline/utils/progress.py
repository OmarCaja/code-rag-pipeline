from llama_index.core import Settings
from rich.console import Console


def count_tokens(text: str) -> int:
    return len(Settings.tokenizer(text))


def show_token_bar(used: int, total: int, console: Console, width: int = 30) -> None:
    filled = int(used / total * width) if total else 0
    bar = "█" * filled + "░" * (width - filled)
    console.print(f"[dim]Tokens: {used}/{total}[/dim] {bar}")
