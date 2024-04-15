import datetime
import logging
import sys
import traceback
from logging.handlers import TimedRotatingFileHandler

from ecjtu.utils import get_default_storage_path
from ecjtu.utils.singleton import Singleton


def get_log_path() -> str:
    log_directory = get_default_storage_path("logs")
    current_time = datetime.datetime.now().strftime("%Y%m%d")
    return f"{log_directory}/{current_time}.log"


class LogManager(metaclass=Singleton):
    def __init__(self) -> None:
        self.logger = logging.getLogger("ecjtu")
        self.logger.setLevel(logging.DEBUG)

        file_handler = TimedRotatingFileHandler(
            filename=get_log_path(), when="midnight", interval=1, encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",  # noqa
            "%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)


def exception_handler(exc_type, exc_value, exc_traceback):
    """
    Handles uncaught exceptions in the program.

    This function is designed to be used as a custom exception handler. It logs the
    details of uncaught exceptions and allows the program to continue running.
    Exceptions derived from KeyboardInterrupt are not handled by this function and are
    instead passed to the default Python exception handler.

    Args:
        exc_type: The type of the exception.
        exc_value: The instance of the exception.
        exc_traceback: A traceback object encapsulating the call stack at
        the point where the exception originally occurred.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    tb_info = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logger.error(f"Uncaught exception: {tb_info}")

    sys.__excepthook__(exc_type, exc_value, exc_traceback)


log_manager = LogManager()
logger = log_manager.logger
original_excepthook = sys.excepthook
sys.excepthook = exception_handler
