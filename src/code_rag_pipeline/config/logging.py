import logging
from typing import Final

import colorlog

THIRD_PARTY_LOGGERS: Final[dict[str, int]] = {
    "httpx": logging.WARNING,
    "httpcore": logging.WARNING,
    "urllib3": logging.WARNING,
    "asyncio": logging.WARNING,
    "llama_index": logging.WARNING,
    "llama_index.core.readers.file.base": logging.ERROR,
    "fsspec.local": logging.WARNING,
}


def setup_logging(default_level: int = logging.DEBUG) -> None:
    """Configures the root logger with full-line colored output."""
    handler: colorlog.StreamHandler = colorlog.StreamHandler()

    formatter = colorlog.ColoredFormatter(
        "%(log_color)s %(asctime)s -> %(levelname)s -> %(name)-25s -> %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(default_level)

    # Prevent duplicate handlers if setup_logging is called multiple times
    if not root_logger.handlers:
        root_logger.addHandler(handler)

    # Silence noisy third-party modules globally
    for logger_name, log_level in THIRD_PARTY_LOGGERS.items():
        logging.getLogger(logger_name).setLevel(log_level)
