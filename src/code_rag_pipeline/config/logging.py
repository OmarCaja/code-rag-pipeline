import logging

import colorlog

THIRD_PARTY_LOGGERS = {
    "httpx": logging.WARNING,
    "httpcore": logging.WARNING,
    "urllib3": logging.WARNING,
    "asyncio": logging.WARNING,
    "llama_index": logging.WARNING,
    "llama_index.core.readers.file.base": logging.ERROR,
    "fsspec.local": logging.WARNING,
}


def setup_logging(default_level: int = logging.DEBUG) -> None:
    handler = colorlog.StreamHandler()
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

    root = logging.getLogger()
    root.setLevel(default_level)
    if not root.handlers:
        root.addHandler(handler)

    for name, level in THIRD_PARTY_LOGGERS.items():
        logging.getLogger(name).setLevel(level)
