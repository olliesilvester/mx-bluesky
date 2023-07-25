import json
from unittest.mock import mock_open, patch

import pytest

from mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1 import (
    cs_maker,
    cs_reset,
    moveto,
    scrape_mtr_directions,
    scrape_mtr_fiducials,
)

mtr_dir_str = """#Some words
mtr1_dir=1
mtr2_dir=-1
mtr3_dir=-1"""

fiducial_1_str = """MTR RBV RAW Corr f_value
MTR1 0 0 1 0
MTR2 1 -1 -1 1
MTR3 0 0 -1 0"""

cs_json = '{"scalex":1, "scaley":2, "scalez":3, "skew":-0.5, "Sx_dir":1, "Sy_dir":-1, "Sz_dir":0}'


@patch("mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1.caput")
@patch("mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1.caget")
def test_moveto_oxford_origin(fake_caget, fake_caput):
    fake_caget.return_value = 0
    moveto(place="origin")
    assert fake_caget.call_count == 1
    assert fake_caput.call_count == 2


@patch("mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1.caput")
@patch("mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1.caget")
def test_moveto_oxford_inner_f1(fake_caget, fake_caput):
    fake_caget.return_value = 1
    moveto(place="f1")
    assert fake_caget.call_count == 1
    assert fake_caput.call_count == 2


@patch("mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1.caput")
@patch("mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1.caget")
def test_moveto_chip_unknown(fake_caget, fake_caput):
    fake_caget.return_value = 4
    moveto(place="zero")
    assert fake_caget.call_count == 1
    assert fake_caput.call_count == 1


@patch(
    "mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1.open",
    mock_open(read_data=mtr_dir_str),
)
def test_scrape_mtr_directions():
    res = scrape_mtr_directions()
    assert len(res) == 3
    assert res == (1.0, -1.0, -1.0)


@patch(
    "mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1.open",
    mock_open(read_data=fiducial_1_str),
)
def test_scrape_mtr_fiducials():
    res = scrape_mtr_fiducials(1)
    assert len(res) == 3
    assert res == (0.0, 1.0, 0.0)


@patch("mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1.caput")
def test_cs_reset(fake_caput):
    cs_reset()
    assert fake_caput.call_count == 4


@patch(
    "mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1.open",
    mock_open(read_data='{"a":11, "b":12,}'),
)
@patch("mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1.caput")
@patch("mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1.caget")
@patch(
    "mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1.scrape_mtr_directions"
)
@patch(
    "mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1.scrape_mtr_fiducials"
)
def test_cs_maker_raises_error_for_invalid_json(
    fake_fid,
    fake_dir,
    fake_caget,
    fake_caput,
):
    fake_dir.return_value = (1, 1, 1)
    fake_fid.return_value = (0, 0, 0)
    with pytest.raises(json.JSONDecodeError):
        cs_maker()


@patch(
    "mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1.open",
    mock_open(read_data='{"scalex":11, "skew":12}'),
)
@patch("mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1.caput")
@patch("mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1.caget")
@patch(
    "mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1.scrape_mtr_directions"
)
@patch(
    "mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1.scrape_mtr_fiducials"
)
def test_cs_maker_raises_error_for_missing_key_in_json(
    fake_fid,
    fake_dir,
    fake_caget,
    fake_caput,
):
    fake_dir.return_value = (1, 1, 1)
    fake_fid.return_value = (0, 0, 0)
    with pytest.raises(KeyError):
        cs_maker()


@patch(
    "mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1.open",
    mock_open(read_data=cs_json),
)
@patch("mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1.caput")
@patch("mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1.caget")
@patch(
    "mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1.scrape_mtr_directions"
)
@patch(
    "mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1.scrape_mtr_fiducials"
)
def test_cs_maker_raises_error_for_wrong_direction_in_json(
    fake_fid,
    fake_dir,
    fake_caget,
    fake_caput,
):
    fake_dir.return_value = (1, 1, 1)
    fake_fid.return_value = (0, 0, 0)
    with pytest.raises(ValueError):
        cs_maker()
