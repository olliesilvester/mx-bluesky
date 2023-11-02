from unittest.mock import patch

from mx_bluesky.I24.serial.setup_beamline.setup_detector import get_detector_type


@patch("mx_bluesky.I24.serial.setup_beamline.setup_detector.caget")
def test_get_detector_type(fake_caget):
    fake_caget.return_value = -22
    assert get_detector_type().name == "eiger"


@patch("mx_bluesky.I24.serial.setup_beamline.setup_detector.caget")
def test_get_detector_type_finds_pilatus(fake_caget):
    fake_caget.return_value = 566
    assert get_detector_type().name == "pilatus"
