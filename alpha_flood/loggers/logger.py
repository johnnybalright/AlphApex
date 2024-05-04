"""
This module contains a function that configures
and initializes a logger for the application.
"""
import logging
from configs.config import LOG_DIR
import os


def setup_logger(name, log_file_name):
    """
    Configures and returns a Logger object.
    The logger is set up to write debug-level
    messages to
    """
    logger_0 = logging.getLogger(name)
    logger_0.setLevel(logging.DEBUG)
    log_file_path = LOG_DIR / f"{log_file_name}.log"
    with open(log_file_path, "w", encoding='utf-8'):
        pass
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.DEBUG)
    log_fmt = "%(asctime)s.%(msecs)03d - %(filename)s:%(lineno)d - %(levelname)s - %(message)s"
    date_fmt = '%Y-%m-%dT%H:%M:%S'
    formatter = logging.Formatter(fmt=log_fmt, datefmt=date_fmt)
    file_handler.setFormatter(formatter)
    logger_0.addHandler(file_handler)
    logger_0.propagate = False
    return logger_0
