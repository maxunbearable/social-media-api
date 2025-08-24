import logging
from logging.config import dictConfig
from pathlib import Path

from api.config import config as app_config, DevConfig

def obfuscated(value: str, length: int) -> str:
    if "@" not in value:
        return value[:length] + "*" * (len(value) - length)
    
    characters = value[:length]
    if "@" not in characters:
        return characters + "*" * (len(value) - length)
    
    first, last = characters.split("@", 1)
    return first + ("*" * (len(value) - length)) + "@" + last

class EmailObfuscationFilter(logging.Filter):
    def __init__(self, name: str, obfuscated_length: int = 4):
        super().__init__(name)
        self.obfuscated_length = obfuscated_length

    def filter(self, record: logging.LogRecord) -> bool:
        if "email" in record.__dict__:
            record.email = obfuscated(record.email, self.obfuscated_length)
        return True

handlers = ["default", "rotating_file"] if isinstance(app_config, DevConfig) else ["default", "rotating_file", "logtail"]

def configure_logging():
    logs_dir = Path(__file__).resolve().parent.parent / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    is_dev = isinstance(app_config, DevConfig)

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "correlation_id": {
                    "()": "asgi_correlation_id.CorrelationIdFilter",
                    "uuid_length": 8 if is_dev else 32,
                    "default_value": "-",
                },
                "email": {
                    "()": EmailObfuscationFilter,
                    "name": "email",
                    "obfuscated_length": 2 if is_dev else 4,
                },
            },
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "format": "(%(correlation_id)s) %(asctime)s %(levelname)-8s %(name)s - %(message)s",
                },
                "file": {
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "format": "%(asctime)s %(levelname)s %(correlation_id)s %(name)s:%(lineno)d %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG" if is_dev else "INFO",
                    "formatter": "console",
                    "filters": ["correlation_id", "email"],
                },
                "rotating_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG" if is_dev else "INFO",
                    "formatter": "file",
                    "filename": str(logs_dir / "app.log"),
                    "maxBytes": 5 * 1024 * 1024,
                    "backupCount": 5,
                    "encoding": "utf-8",
                    "filters": ["correlation_id"],
                },
                "logtail": {
                    "class": "logtail.LogtailHandler",
                    "level": "DEBUG" if is_dev else "INFO",
                    "formatter": "console",
                    "filters": ["correlation_id", "email"],
                    "source_token": app_config.LOGTAIL_API_KEY,
                    "host": "https://s1486720.eu-nbg-2.betterstackdata.com",
                },
            },
            "root": {
                "handlers": ["default", "rotating_file", "logtail"],
                "level": "DEBUG" if is_dev else "INFO",
            },
            "loggers": {
                "api": {
                    "handlers": handlers,
                    "level": "DEBUG" if is_dev else "INFO",
                    "propagate": False,
                },
                "uvicorn": {
                    "handlers": handlers,
                    "level": "INFO",
                },
                "databases": {
                    "handlers": handlers,
                    "level": "WARNING",
                },
                "aiosqlite": {
                    "handlers": handlers,
                    "level": "WARNING",
                },
                "urllib3": {
                    "handlers": handlers,
                    "level": "WARNING",
                },
            },
        }
    )