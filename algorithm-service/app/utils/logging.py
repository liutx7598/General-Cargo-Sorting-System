import logging

from app.core.config import get_settings


def get_logger(name: str) -> logging.Logger:
    """Create a module logger using service settings."""
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    return logging.getLogger(name)

