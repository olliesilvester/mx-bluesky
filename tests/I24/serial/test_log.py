import logging
from unittest.mock import patch

import pytest

from mx_bluesky.I24.serial import log


@pytest.fixture
def dummy_logger():
    logger = logging.getLogger("I24ssx")
    yield logger


@patch("mx_bluesky.I24.serial.log.environ")
@patch("mx_bluesky.I24.serial.log.Path.mkdir")
def test_logging_file_path(mock_dir, mock_environ):
    mock_environ.get.return_value = None
    log_path = log._get_logging_file_path()
    assert mock_dir.call_count == 1
    assert log_path.as_posix() == "tmp/logs"


@patch("mx_bluesky.I24.serial.log.environ")
@patch("mx_bluesky.I24.serial.log.Path.mkdir")
def test_logging_file_path_on_beamline(mock_dir, mock_environ):
    mock_environ.get.return_value = "i24"
    log_path = log._get_logging_file_path()
    assert mock_dir.call_count == 1
    assert log_path.as_posix() == "/dls_sw/i24/logs/serial"


def test_basic_logging_config(dummy_logger):
    assert dummy_logger.hasHandlers() is True
    assert len(dummy_logger.handlers) == 1
    assert dummy_logger.handlers[0].level == logging.DEBUG


@patch("mx_bluesky.I24.serial.log.Path.mkdir")
@patch("mx_bluesky.I24.serial.log.set_up_all_logging_handlers")
@patch("mx_bluesky.I24.serial.log.integrate_bluesky_and_ophyd_logging")
def test_logging_config_with_filehandler(
    mock_ophyd_log, mock_handlers, mock_dir, dummy_logger
):
    # dodal handlers mocked out
    log.config("dummy.log", delayed=True, dev_mode=True)
    assert len(dummy_logger.handlers) == 2
    assert mock_dir.call_count == 2
    assert dummy_logger.handlers[1].level == logging.DEBUG
    # Clear FileHandler to avoid other tests failing if it is kept open
    dummy_logger.removeHandler(dummy_logger.handlers[1])
