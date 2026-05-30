"""Centralised logger for AgentCrew."""
from __future__ import annotations

import logging
import sys

_FORMATTER = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
_HANDLER = logging.StreamHandler(sys.stdout)
_HANDLER.setFormatter(_FORMATTER)

_root = logging.getLogger("agentcrew")
_root.setLevel(logging.INFO)
if not _root.handlers:
    _root.addHandler(_HANDLER)


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the 'agentcrew' namespace."""
    return logging.getLogger(name)


def set_log_level(level: int | str) -> None:
    """Adjust verbosity for all AgentCrew loggers."""
    _root.setLevel(level)
