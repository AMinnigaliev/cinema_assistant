import logging

__all__ = ["logger"]

from core import config


def get_logger(
    log_format: str = "%(asctime)s - %(levelname)s - %(message)s",
) -> logging.Logger:
    logger_ = logging.getLogger()
    logger_.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(f"{config.base_dir}/logs/app.log")
    formatter = logging.Formatter(log_format)

    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger_.addHandler(console_handler)
    logger_.addHandler(file_handler)

    return logger_


logger = get_logger()
