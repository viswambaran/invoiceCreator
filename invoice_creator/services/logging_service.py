from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from invoice_creator.services.app_paths import logs_directory

_CONFIGURED = False


def configure_logging() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    directory = logs_directory()
    directory.mkdir(parents=True, exist_ok=True)
    log_path = directory / "invoice_creator.log"

    handler = RotatingFileHandler(
        log_path,
        maxBytes=2_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)
    _CONFIGURED = True
