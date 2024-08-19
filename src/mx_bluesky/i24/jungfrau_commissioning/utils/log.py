import logging
import os
from pathlib import Path

from dodal.log import LOGGER as dodal_logger
from dodal.log import set_up_all_logging_handlers as setup_dodal_logging

LOGGER = logging.getLogger("jungfrau_commissioning")
LOGGER.setLevel(logging.DEBUG)
LOGGER.parent = dodal_logger
LOGGING_DIR = "/tmp/jungfrau_commissioning_logs2"


def set_up_logging_handlers(
    logging_level: str | None = "INFO",
    dev_mode: bool = True,
    file_handler_log_level="DEBUG",
):
    """Set up the logging level and instances for user chosen level of logging.

    Mode defaults to production and can be switched to dev with the --dev flag on run.
    """
    if not os.path.isdir(LOGGING_DIR):
        os.makedirs(LOGGING_DIR)
    handlers = setup_dodal_logging(
        logger=LOGGER,
        logging_path=Path(LOGGING_DIR),
        filename="jungfrau_commissioning.log",
        dev_mode=dev_mode,
        error_log_buffer_lines=50000,
        graylog_port=None,
    )

    return handlers
