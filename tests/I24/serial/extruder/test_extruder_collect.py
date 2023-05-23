from unittest.mock import patch

from mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2 import (
    initialise_extruderi24,
    scrape_parameter_file,
)


def test_scrape_parameter_file():
    res = scrape_parameter_file()
    assert len(res) == 10


@patch("mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.caput")
def test_initialise_extruder(fake_caput):
    initialise_extruderi24()
    assert fake_caput.call_count == 11
