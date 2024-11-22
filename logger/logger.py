import logging
import sys
import os
from datetime import date

# ANSI color codes
RESET = "\033[0m"
BLUE = "\033[94m"
LEVEL_COLORS = {
    "DEBUG": "\033[37m",      # White
    "INFO": "\033[95m",
    "WARNING": "\033[93m",
    "ERROR": "\033[91m",      # Red
    "CRITICAL": "\033[41m",   # White on Red background
    "SUCCESS": "\033[92m",    # Green
}

LEVEL_WIDTH = {
    'DEBUG': 8,
    'INFO': 8,
    'SUCCESS': 8,
    'WARNING': 8,
    'ERROR': 8,
    'CRITICAL': 9
}

SUCCESS_LEVEL = 25
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")

class CustomFormatter(logging.Formatter):
    def format(self, record):

        log_color = LEVEL_COLORS.get(record.levelname, RESET)

        if record.levelname == 'SUCCESS' or record.levelname == 'ERROR':
            record.msg = f"{log_color}{record.msg}{RESET}"

        record.levelname = f"{log_color}{record.levelname:<{LEVEL_WIDTH[record.levelname]}}{RESET}"
        return super().format(record)

def setup_logger():
    logger = logging.getLogger("my_logger")
    logger.setLevel(logging.DEBUG)

    # Formatter with colors
    formatter = CustomFormatter(
        "%(asctime)s | %(levelname)s | %(message)s", datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File handler without colors
    os.makedirs('logs', exist_ok=True)

    file_handler = logging.FileHandler(f"logs/out_{date.today().strftime('%m-%d')}.log")
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
    )
    
    logger.addHandler(file_handler)

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    def success(self, message, *args, **kwargs):
        if self.isEnabledFor(SUCCESS_LEVEL):
            self._log(SUCCESS_LEVEL, message, args, **kwargs)

    logging.Logger.success = success

    return logger

logger = setup_logger()