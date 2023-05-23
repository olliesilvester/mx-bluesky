import pytest

from mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_StartUp_py3v1 import (
    fiducials,
    get_format,
)

# scrape_parameter_file, # avoid because currently in use


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
