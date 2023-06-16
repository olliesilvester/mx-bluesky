from unittest.mock import patch

from mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1 import moveto


@patch("mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1.caput")
@patch("mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1.caget")
def test_moveto_oxford_origin(fake_caget, fake_caput):
    fake_caget.return_value = 1
    moveto("origin")
    assert fake_caget.call_count == 1
    assert fake_caput.call_count == 2


@patch("mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1.caput")
@patch("mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1.caget")
def test_moveto_chip_unknown(fake_caget, fake_caput):
    fake_caget.return_value = 2
    moveto("yag")
    assert fake_caget.call_count == 1
    assert fake_caput.call_count == 3
