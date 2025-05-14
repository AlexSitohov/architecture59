import logging
import sys
from typing import Optional


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def log_execution_time(
    logger: logging.Logger,
    start_time: float,
    end_time: float,
    operation: str,
    extra_info: Optional[dict] = None,
) -> None:

    execution_time = end_time - start_time
    message = f"Операция '{operation}' выполнена за {execution_time:.2f} секунд"

    if extra_info:
        extra_details = ", ".join([f"{k}: {v}" for k, v in extra_info.items()])
        message += f" ({extra_details})"

    logger.info(message)
