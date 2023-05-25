from unittest.mock import mock_open, patch

from mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2 import (
    initialise_extruderi24,
    moveto,
    scrape_parameter_file,
)

FAKE_PARAM_FILE = "tests/I24/serial/EX_param_file.txt"


def get_test_params():
    with open(FAKE_PARAM_FILE, "r") as f:
        params = f.read()
    return params


@patch(
    "mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.open",
    mock_open(read_data=get_test_params()),
)
def test_scrape_parameter_file():
    res = scrape_parameter_file()
    assert res[0] == "foo"
    assert len(res) == 10


@patch("mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.caput")
def test_initialise_extruder(fake_caput):
    initialise_extruderi24()
    assert fake_caput.call_count == 11


@patch("mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.caput")
@patch("mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.caget")
def test_moveto(fake_caput, fake_caget):
    moveto("enterhutch")
    assert fake_caget.call_count == 1
    assert fake_caput.call_count == 1
