from __future__ import annotations

import functools
import logging
import logging.config
from os import environ
from pathlib import Path
from typing import Optional

from dodal.log import (
    ERROR_LOG_BUFFER_LINES,
    integrate_bluesky_and_ophyd_logging,
    set_up_all_logging_handlers,
)
from dodal.log import LOGGER as dodal_logger

# Logging set up
logging.getLogger("I24ssx").addHandler(logging.NullHandler())
logging.getLogger("I24ssx").parent = dodal_logger

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "class": "logging.Formatter",
            "format": "%(message)s",
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        }
    },
    "loggers": {
        "I24ssx": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        }
    },
}

logging.config.dictConfig(logging_config)


def _get_logging_file_path() -> Path:
    """Get the path to write the artemis log files to.
    If on a beamline, this will be written to the according area depending on the
    BEAMLINE envrionment variable. If no envrionment variable is found it will default
    it to the tmp/dev directory.
    Returns:
        logging_path (Path): Path to the log file for the file handler to write to.
    """
    beamline: Optional[str] = environ.get("BEAMLINE")
    logging_path: Path

    if beamline:
        logging_path = Path("/dls_sw/" + beamline + "/logs/serial/")
    else:
        logging_path = Path("./tmp/logs/")

    try:
        Path(logging_path).mkdir(parents=True, exist_ok=True)
    except OSError:
        # Until https://github.com/DiamondLightSource/mx_bluesky/issues/45 is fixed
        # Logs could also go to the current visit directory, but not always possible
        # when testing
        logging_path = Path("~/serial_logs/").expanduser().resolve()
        Path(logging_path).mkdir(parents=True, exist_ok=True)
    return logging_path


def config(
    logfile: str | None = None,
    write_mode: str = "a",
    delayed: bool = False,
    dev_mode: bool = False,
):
    """
    Configure the logging.

    Args:
        logfile (str, optional): Filename for logfile. If passed, create a file handler\
            for the logger to write to file the log output. Defaults to None.
        write_mode (str, optional): String indicating writing mode for the output \
            .log file. Defaults to "a".
        dev_mode (bool, optional): If true, will log to graylog on localhost instead \
            of production. Defaults to False.
    """
    logger = logging.getLogger("I24ssx")
    handlers = set_up_all_logging_handlers(
        dodal_logger,
        _get_logging_file_path(),
        "dodal.log",
        dev_mode,
        ERROR_LOG_BUFFER_LINES,
    )
    integrate_bluesky_and_ophyd_logging(dodal_logger, handlers)

    if logfile:
        logs = _get_logging_file_path() / logfile
        fileFormatter = logging.Formatter(
            "%(asctime)s %(levelname)s: \t(%(name)s) %(message)s",
            datefmt="%d-%m-%Y %I:%M:%S",
        )
        FH = logging.FileHandler(logs, mode=write_mode, encoding="utf-8", delay=delayed)
        FH.setLevel(logging.DEBUG)
        FH.setFormatter(fileFormatter)
        logger.addHandler(FH)


def log_on_entry(func):
    logger = logging.getLogger("I24ssx")

    @functools.wraps(func)
    def decorator(*args, **kwargs):
        name = func.__name__
        logger.debug("Running %s " % name)
        return func(*args, **kwargs)

    return decorator
