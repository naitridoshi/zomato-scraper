import logging
import queue
import sys
from logging.handlers import QueueListener
from time import sleep
from enum import Enum


class LogColors:
    INFO = "\033[92m"  # Green
    DEBUG = "\033[94m"  # Blue
    WARNING = "\033[93m"  # Yellow
    ERROR = "\033[91m"  # Red
    RESET = "\033[0m"  # Reset to default


class Colors(Enum):
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright Colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    RESET = "\033[0m"


def color_string(message, color: Colors = Colors.CYAN):
    return f"{color.value}{str(message)}{Colors.RESET.value}"


# Custom formatter to add colors
class ColoredFormatter(logging.Formatter):
    def format(self, record):
        log_colors = {
            logging.INFO: LogColors.INFO,
            logging.DEBUG: LogColors.DEBUG,
            logging.WARNING: LogColors.WARNING,
            logging.ERROR: LogColors.ERROR,
        }
        color = log_colors.get(record.levelno, LogColors.RESET)
        record.levelname = f"{color}{record.levelname}{LogColors.RESET}"
        return super().format(record)


# Create formatter
console_format = ColoredFormatter(
    fmt=" ".join(
        [
            f"\033[35m%(asctime)s{LogColors.RESET} |",
            "%(name)s |",
            "%(levelname)s |",
            "message: %(message)s",
        ]
    )
)

file_format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - message: %(message)s"
)


def get_logger(
    name: str = "utils",
    queue_logs: bool = True,
):
    logger = logging.getLogger(name)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(console_format)

    # Remove all handlers associated with the logger
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(logging.DEBUG)
    if queue_logs:
        log_queue = queue.Queue() # type: ignore
        queue_handler = logging.handlers.QueueHandler(log_queue)
        logger.addHandler(queue_handler)
        handlers = list()
        handlers.append(console_handler)

        # Use console_handler only in the listener
        listener = QueueListener(log_queue, *handlers, respect_handler_level=True)
        return logger, listener

    logger.addHandler(console_handler)
    return logger


def suppress_all_loggers():
    """
    Suppress all loggers by replacing their handlers with NullHandler and disabling propagation.
    Call this at the start of your test suite to silence all logs.
    """
    import logging

    root_logger = logging.getLogger()
    root_logger.handlers = [logging.NullHandler()]
    root_logger.propagate = False
    for logger_name in logging.root.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        logger.handlers = [logging.NullHandler()]
        logger.propagate = False


def suppress_external_loggers():
    """
    Suppress only external loggers (httpx, mem0) by setting their log level to WARNING.
    Call this at the start of your test suite to silence noisy third-party logs but keep your logs visible.
    """
    import logging

    for ext_logger in [
        "httpx",
        "mem0",
        "mem0.vector_stores.qdrant",
        "mem0.memory.graph_memory",
    ]:
        logging.getLogger(ext_logger).setLevel(logging.WARNING)


if __name__ == "__main__":
    test_logger, test_listener = get_logger("test")
    test_listener.start()

    test_logger.info("Test message for thread-safe logging")

    sleep(1)
    test_listener.stop()  # Properly stop the listener when done