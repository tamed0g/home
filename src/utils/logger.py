import logging
import sys
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.logging import RichHandler

# Исправлено: импорт config из родительского пакета
from ..config import config


def setup_logging(
    log_level: str = None,
    log_file: str = None,
    use_rich: bool = True,
) -> logging.Logger:
    
    log_level = log_level or config.LOG_LEVEL
    log_file = log_file or config.LOG_FILE

    log_path = config.BASE_DIR / log_file
    log_path.parent.mkdir(parents=True, exist_ok=True)

    level = getattr(logging, log_level.upper(), logging.INFO)

    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    handlers = []

    file_handler = logging.FileHandler(log_path, encoding="UTF-8")
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(level)
    handlers.append(file_handler)

    if use_rich and config.is_development():
        console_handler = RichHandler(
            console=Console(stderr=True),
            show_time=True,
            show_path=True,
            markup=True,
            rich_tracebacks=True
        )
        console_handler.setLevel(level)
    else:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(file_formatter)
        console_handler.setLevel(level)

    handlers.append(console_handler)

    logging.basicConfig(
        level=level,
        handlers=handlers,
        force=True
    )

    return logging.getLogger(config.APP_NAME)

# Исправлено: переименована функция setup_loggin -> setup_logging
logger = setup_logging()

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"{config.APP_NAME}.{name}")