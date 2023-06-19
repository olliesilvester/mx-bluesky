import logging
from unittest.mock import patch

from mx_bluesky.I24.serial import log


@patch("mx_bluesky.I24.serial.log.Path.mkdir")
def test_logging_file_path(mock_dir):
    log_path = log._get_logging_file_path()
    assert mock_dir.call_count == 1
    assert log_path.as_posix() == "tmp/logs"


def test_basic_logging_config():
    logger = logging.getLogger("I24ssx")
    assert logger.hasHandlers() is True
    assert len(logger.handlers) == 1
