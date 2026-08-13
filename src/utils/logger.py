import logging

import colorlog


def setup_logging(default_level: int = logging.DEBUG) -> None:
    """Configures the root logger with colored output and filters noisy libraries."""
    handler: colorlog.StreamHandler = colorlog.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s [%(levelname)s] %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
    )

    # Configure Root Logger
    root_logger = logging.getLogger()
    root_logger.setLevel(default_level)

    # Avoid adding multiple duplicate handlers if called twice
    if not root_logger.handlers:
        root_logger.addHandler(handler)

    # Silence noisy third-party modules globally
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("llama_index").setLevel(logging.INFO)
