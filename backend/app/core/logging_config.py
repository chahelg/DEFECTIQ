"""
Logging configuration
"""

import logging
import logging.config
from pathlib import Path
from app.core.config import settings
import json
from datetime import datetime

# Create logs directory
log_dir = Path(settings.LOG_DIR)
log_dir.mkdir(exist_ok=True)

# JSON logging formatter
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "json": {
            "()": JSONFormatter,
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "formatter": "json" if settings.LOG_FORMAT == "json" else "default",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": settings.LOG_FILE,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
    },
    "loggers": {
        "app": {
            "handlers": ["default", "file"],
            "level": settings.LOG_LEVEL,
        },
        "uvicorn": {
            "handlers": ["default", "file"],
            "level": settings.LOG_LEVEL,
        },
        "sqlalchemy": {
            "handlers": ["default", "file"],
            "level": "WARNING",
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

