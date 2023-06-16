import logging
from unittest.mock import patch

import pytest

from mx_bluesky.I24.serial import log


@pytest.fixture
def dummy_logger():
    logger = logging.getLogger("I24ssx.dummy")
    yield logger


@patch("mx_bluesky.I24.serial.log.Path.mkdir")
def test_logging_file_path(mock_dir):
    log_path = log._get_logging_file_path()
    assert mock_dir.call_count == 1
    assert log_path.as_posix() == "tmp/logs"


@patch("mx_bluesky.I24.serial.log.Path.mkdir")
@patch("mx_bluesky.I24.serial.log.logging.FileHandler")
def test_log_config(mock_fh, mock_dir, dummy_logger):
    log.config("dummy.log")
    assert mock_fh.call_count == 1
