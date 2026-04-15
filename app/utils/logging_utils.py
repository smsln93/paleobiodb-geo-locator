import logging
import os
import datetime
from typing import Optional
from app.config.config_paths import LOG_DIR


TIMESTAMP = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
LOG_FORMAT = logging.Formatter('[%(levelname)s] %(asctime)s - %(name)s : %(message)s')


def setup_logger(log_to_file: bool = False, debug: bool = False) -> logging.Logger:
    """
    Sets up and returns a logger.

    :param log_to_file: If True, enables logging to a file in the logs/ directory.
    :param debug: If True, sets the logger level as DEBUG.
    :return: Configured logging.Logger instance.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if debug else logging.INFO)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(LOG_FORMAT)
    handlers: list = [stream_handler]

    if log_to_file:
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR, exist_ok=True)

        file_handler = logging.FileHandler(os.path.join(LOG_DIR, f'{TIMESTAMP}.log'), mode='w+')
        file_handler.setFormatter(LOG_FORMAT)
        handlers.append(file_handler)

    for handler in handlers:
        if all(not isinstance(h, type(handler)) for h in logger.handlers):
            logger.addHandler(handler)

    return logger


def get_log_path(current_logger: logging.Logger) -> Optional[str]:
    """
    Returns the file path of the FileHandler that is attached to the given logger.

    :param current_logger: The logger object to inspect.
    :return: Full path to the log file if a FileHandler is present, or None otherwise.
    """
    for handler in current_logger.handlers:
        if isinstance(handler, logging.FileHandler):
            return handler.baseFilename
    return None
