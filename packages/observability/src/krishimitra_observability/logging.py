from __future__ import annotations
import logging
import sys

def configure_logging(level: str = "INFO", json_format: bool = False) -> None:
    fmt = "%(asctime)s %(levelname)s %(name)s %(message)s"
    if json_format:
        fmt = '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","msg":"%(message)s"}'
    logging.basicConfig(stream=sys.stdout, level=getattr(logging, level.upper(), logging.INFO), format=fmt)

__all__ = ["configure_logging"]
