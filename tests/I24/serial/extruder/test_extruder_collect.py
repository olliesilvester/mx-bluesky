from unittest.mock import mock_open, patch

from mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2 import (
    initialise_extruderi24,
    moveto,
    run_extruderi24,
    scrape_parameter_file,
)

params_file_str = "visit foo \ndirectory bar \nfilename boh \nnum_imgs 1  \
    \nexp_time 0.1 \ndet_dist 100 \ndet_type eiger \npump_probe false \
    \npump_exp 0 \npump_delay 0"


@patch(
    "mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.open",
    mock_open(read_data=params_file_str),
)
def test_scrape_parameter_file():
    res = scrape_parameter_file()
    assert res[0] == "foo"
    assert len(res) == 10


@patch("mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.caput")
@patch("mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.caget")
def test_initialise_extruder(fake_caget, fake_caput):
    initialise_extruderi24()
    assert fake_caget.call_count == 2
    assert fake_caput.call_count == 11


@patch("mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.caput")
@patch("mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.caget")
def test_moveto(fake_caget, fake_caput):
    moveto("enterhutch")
    assert fake_caget.call_count == 1
    assert fake_caput.call_count == 1


@patch(
    "mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.open",
    mock_open(read_data=params_file_str),
)
@patch("mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.DCID")
@patch("mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.call_nexgen")
@patch("mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.caput")
@patch("mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.caget")
@patch("mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.sup")
def test_run_extruder(fake_sup, fake_caget, fake_caput, fake_nexgen, fake_dcid):
    run_extruderi24()
    assert fake_nexgen.call_count == 1
