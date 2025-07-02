
import logging
import logging.config
import sys
from typing import Dict, Any

LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s%(levelname)-8s%(reset)s %(name)-20s %(message)s",
            "log_colors": {
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        },
        "file": {
            "format": "%(asctime)s %(levelname)-8s %(name)-20s %(message)s",
        },
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "INFO",
            "stream": sys.stdout,
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "file",
            "filename": "partybot.log",
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5,
            "level": "DEBUG",
        },
    },
    "root": {"handlers": ["default", "file"], "level": "DEBUG"},
}


class UserIDFilter(logging.Filter):
    """A logging filter to redact user IDs."""

    def filter(self, record: logging.LogRecord) -> bool:
        if hasattr(record, "user_id"):
            record.msg = record.msg.replace(str(record.user_id), "[REDACTED]")
        return True


def setup_logging():
    """Sets up the logging configuration."""
    try:
        import colorlog
    except ImportError:
        # If colorlog is not installed, use a standard formatter
        LOGGING_CONFIG["formatters"]["default"] = {
            "format": "%(levelname)-8s %(name)-20s %(message)s"
        }
        LOGGING_CONFIG["handlers"]["default"]["formatter"] = "default"

    logging.config.dictConfig(LOGGING_CONFIG)
    logging.getLogger().addFilter(UserIDFilter())


def get_logger(name: str) -> logging.Logger:
    """Gets a logger with the given name."""
    return logging.getLogger(name)
