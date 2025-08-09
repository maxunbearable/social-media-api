from logging.config import dictConfig
from pathlib import Path

from api.config import config as app_config, DevConfig


def configure_logging():
    logs_dir = Path(__file__).resolve().parent.parent / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    is_dev = isinstance(app_config, DevConfig)

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "format": "%(asctime)s %(levelname)-8s %(name)s - %(message)s",
                },
                "file": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "format": "%(asctime)s %(levelname)-8s %(name)s:%(lineno)d - %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG" if is_dev else "INFO",
                    "formatter": "console",
                },
                "rotating_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG" if is_dev else "INFO",
                    "formatter": "file",
                    "filename": str(logs_dir / "app.log"),
                    "maxBytes": 5 * 1024 * 1024,
                    "backupCount": 5,
                    "encoding": "utf-8",
                },
            },
            "root": {
                "handlers": ["default", "rotating_file"],
                "level": "DEBUG" if is_dev else "INFO",
            },
            "loggers": {
                "api": {
                    "handlers": ["default", "rotating_file"],
                    "level": "DEBUG" if is_dev else "INFO",
                    "propagate": False,
                },
                "uvicorn": {
                    "handlers": ["default", "rotating_file"],
                    "level": "INFO",
                },
                "databases": {
                    "handlers": ["default", "rotating_file"],
                    "level": "WARNING",
                },
                "aiosqlite": {
                    "handlers": ["default", "rotating_file"],
                    "level": "WARNING",
                },
            },
        }
    )