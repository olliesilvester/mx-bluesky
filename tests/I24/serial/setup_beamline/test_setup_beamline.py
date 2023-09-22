from unittest.mock import patch

import pytest

from mx_bluesky.I24.serial.setup_beamline import setup_beamline


@patch("mx_bluesky.I24.serial.setup_beamline.setup_beamline.caget")
def test_get_detector_type(fake_caget):
    fake_caget.return_value = -22
    assert setup_beamline.get_detector_type().name == "eiger"


@patch("mx_bluesky.I24.serial.setup_beamline.setup_beamline.caget")
def test_get_detector_type_finds_pilatus(fake_caget):
    fake_caget.return_value = 566
    assert setup_beamline.get_detector_type().name == "pilatus"


@patch("mx_bluesky.I24.serial.setup_beamline.setup_beamline.caput")
def test_beamline_collect(fake_caput):
    setup_beamline.beamline("collect")
    assert fake_caput.call_count == 4


def test_beamline_raises_error_if_quickshot_and_no_args_list():
    with pytest.raises(TypeError):
        setup_beamline.beamline("quickshot")


@patch("mx_bluesky.I24.serial.setup_beamline.setup_beamline.caput")
@patch("mx_bluesky.I24.serial.setup_beamline.setup_beamline.caget")
def test_beamline_quickshot(fake_caget, fake_caput):
    fake_caget.return_value = 100
    setup_beamline.beamline("quickshot", ["100"])
    assert fake_caput.call_count == 1
    assert fake_caget.call_count == 2


@patch("mx_bluesky.I24.serial.setup_beamline.setup_beamline.caput")
@patch("mx_bluesky.I24.serial.setup_beamline.setup_beamline.caget")
def test_pilatus_raises_error_if_fastchip_and_no_args_list(fake_caget, fake_caput):
    with pytest.raises(TypeError):
        setup_beamline.pilatus("fastchip")


@patch("mx_bluesky.I24.serial.setup_beamline.setup_beamline.caput")
@patch("mx_bluesky.I24.serial.setup_beamline.setup_beamline.caget")
def test_pilatus_quickshot(fake_caget, fake_caput):
    setup_beamline.pilatus("quickshot", ["", "", 1, 0.1])
    assert fake_caput.call_count == 12
    assert fake_caget.call_count == 2


@patch("mx_bluesky.I24.serial.setup_beamline.setup_beamline.caput")
@patch("mx_bluesky.I24.serial.setup_beamline.setup_beamline.caget")
def test_eiger_raises_error_if_quickshot_and_no_args_list(fake_caget, fake_caput):
    with pytest.raises(TypeError):
        setup_beamline.eiger("quickshot")


@patch("mx_bluesky.I24.serial.setup_beamline.setup_beamline.caput")
@patch("mx_bluesky.I24.serial.setup_beamline.setup_beamline.caget")
def test_eiger_quickshot(fake_caget, fake_caput):
    setup_beamline.eiger("quickshot", ["", "", "1", "0.1"])
    assert fake_caput.call_count == 32


@patch("mx_bluesky.I24.serial.setup_beamline.setup_beamline.caput")
def test_zebra1_return_to_normal(fake_caput):
    setup_beamline.zebra1("return-to-normal")
    assert fake_caput.call_count == 20


@patch("mx_bluesky.I24.serial.setup_beamline.setup_beamline.caput")
def test_zebra1_quickshot(fake_caput):
    setup_beamline.zebra1("quickshot", [0, 1])
    assert fake_caput.call_count == 7


@patch("mx_bluesky.I24.serial.setup_beamline.setup_beamline.caput")
def test_zebra1_fastchip_pilatus(fake_caput):
    setup_beamline.zebra1("fastchip-pilatus", [1, 1, 0.1])
    assert fake_caput.call_count == 12


@patch("mx_bluesky.I24.serial.setup_beamline.setup_beamline.caput")
def test_zebra1_fastchip_eiger(fake_caput):
    setup_beamline.zebra1("fastchip-eiger", [1, 1, 0.1])
    assert fake_caput.call_count == 12
