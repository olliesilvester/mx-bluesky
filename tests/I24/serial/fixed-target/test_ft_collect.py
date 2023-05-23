from mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Collect_py3v1 import (
    get_chip_prog_values,
)


def test_get_chip_prog_values():
    chip_dict = get_chip_prog_values(
        "1",
        "i24",
        "0",
        0,
        0,
        0,
    )
    assert type(chip_dict) is dict
