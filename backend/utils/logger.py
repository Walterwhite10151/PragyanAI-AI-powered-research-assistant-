"""
backend/utils/logger.py
-----------------------
Loguru-based structured logger.
- Coloured stderr output for development.
- Rotating JSON log files for production.
"""

import sys
from loguru import logger as _logger
from backend.core.config import settings

_logger.remove()

_logger.add(
    sys.stderr,
    level="INFO",
    format=(
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    ),
    colorize=True,
)

_logger.add(
    f"{settings.logs_path}/agent_{{time:YYYY-MM-DD}}.log",
    level="DEBUG",
    rotation="1 day",
    retention="7 days",
    serialize=True,
)

logger = _logger
