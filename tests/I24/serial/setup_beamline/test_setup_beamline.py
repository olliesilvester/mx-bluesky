from unittest.mock import patch

import pytest

from mx_bluesky.I24.serial.setup_beamline import setup_beamline


def test_beamline_raises_error_if_quickshot_and_no_args_list():
    with pytest.raises(TypeError):
        setup_beamline.beamline("quickshot")


@patch("mx_bluesky.I24.serial.setup_beamline.setup_beamline.caput")
def test_pilatus_raises_error_if_fastchip_and_no_args_list(fake_caput):
    with pytest.raises(TypeError):
        setup_beamline.pilatus("fastchip")


@patch("mx_bluesky.I24.serial.setup_beamline.setup_beamline.caput")
def test_eiger_raises_error_if_quickshot_and_no_args_list(fake_caput):
    with pytest.raises(TypeError):
        setup_beamline.eiger("quickshot")


@patch("mx_bluesky.I24.serial.setup_beamline.setup_beamline.caput")
def test_zebra1_return_to_normal(fake_caput):
    setup_beamline.zebra1("return-to-normal")
    assert fake_caput.call_count == 20
