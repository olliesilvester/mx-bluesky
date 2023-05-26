from unittest.mock import mock_open, patch

import pytest

from mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_StartUp_py3v1 import (
    fiducials,
    get_format,
    scrape_parameter_file,
)

params_file_str = "visit foo \nsub_dir bar \nchip_name chip \nprotein_name protK \
    \nn_exposures 1 \nchip_type 1 \nmap_type None \ndcdetdist 100 \ndet_type eig \
    \nexptime 0.01 \npump_repeat 0 \npumpexptime 0 \nprepumpexptime 0 \npumpdelay 0"


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


def test_fiducials_raises_error_for_chip_type_0():
    # mostly as a reminder this needs fixing because old python
    with pytest.raises(AttributeError):
        fiducials("0")


def test_get_format():
    # oxford chip
    fmt = get_format("1")
    assert fmt == [8, 8, 20, 20, 0.125, 0.800, 0.800]
