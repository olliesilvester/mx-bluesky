from unittest.mock import mock_open, patch

import pytest

from mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_StartUp_py3v1 import (
    check_files,
    fiducials,
    get_format,
    pathli,
    scrape_parameter_file,
)

params_file_str = """visit foo
sub_dir bar
chip_name chip
protein_name protK
n_exposures 1
chip_type 0
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
    res = scrape_parameter_file()
    assert res[0] == "chip"
    assert len(res) == 13


def test_fiducials():
    assert len(fiducials("0")) == 0
    assert len(fiducials("1")) == 0


def test_get_format_for_oxford_chip():
    # oxford chip
    fmt = get_format("0")
    assert fmt == [8, 8, 20, 20, 0.125, 0.800, 0.800]


def test_get_format_for_oxford_minichip():
    # 1 block of oxford chip
    fmt = get_format("3")
    assert fmt == [1, 1, 20, 20, 0.125, 0.0, 0.0]


@patch("mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_StartUp_py3v1.os")
@patch(
    "mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_StartUp_py3v1.open",
    mock_open(read_data=params_file_str),
)
def test_check_files(mock_os):
    check_files("i24", [".a", ".b"])


@pytest.mark.parametrize(
    "list_in, way, reverse, expected_res",
    [
        (
            [1, 2, 3],
            "typewriter",
            False,
            [1, 2, 3] * 3,
        ),  # Result should be list * len(list)
        ([1, 2, 3], "typewriter", True, [3, 2, 1] * 3),  # list[::-1] * len(list)
        ([4, 5], "snake", False, [4, 5, 5, 4]),  # Snakes the list
        ([4, 5], "expand", False, [4, 4, 5, 5]),  # Repeats each value
    ],
)
def test_pathli(list_in, way, reverse, expected_res):
    assert pathli(list_in, way, reverse) == expected_res
