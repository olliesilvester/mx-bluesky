from unittest.mock import mock_open, patch

from mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_StartUp_py3v1 import (
    fiducials,
    get_format,
    scrape_parameter_file,
)

params_file_str = """visit foo
sub_dir bar
chip_name chip
protein_name protK
n_exposures 1
chip_type 1
map_type None
dcdetdist 100
det_type eig
exptime 0.01
pump_repeat 0
pumpexptime 0
prepumpexptime 0
pumpdelay 0"""


@patch(
    "mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_StartUp_py3v1.open",
    mock_open(read_data=params_file_str),
)
def test_scrape_parameter_file():
    res = scrape_parameter_file(location="i24")
    assert res[0] == "chip"
    assert len(res) == 13


def test_fiducials():
    assert len(fiducials("1")) == 0
    assert len(fiducials("5")) == 0
    assert len(fiducials("0")) > 0


def test_get_format():
    # oxford chip
    fmt = get_format("1")
    assert fmt == [8, 8, 20, 20, 0.125, 0.800, 0.800]
