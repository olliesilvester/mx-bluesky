import argparse
from unittest.mock import mock_open, patch

import pytest

from mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2 import (
    initialise_extruderi24,
    moveto,
    run_extruderi24,
    scrape_parameter_file,
)
from mx_bluesky.I24.serial.setup_beamline import Eiger, Pilatus

params_file_str = """visit foo
directory bar
filename boh
num_imgs 1
nexp_time 0.1
det_dist 100
det_type eiger
pump_probe false
pump_exp 0
pump_delay 0"""


@pytest.fixture
def dummy_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "place",
        type=str,
        choices=["laseron", "laseroff", "enterhutch"],
        help="Requested setting.",
    )
    yield parser


@patch(
    "mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.open",
    mock_open(read_data=params_file_str),
)
def test_scrape_parameter_file():
    res = scrape_parameter_file()
    assert res[0] == "foo"
    assert len(res) == 10


@patch("mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.caget")
@patch("mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.caput")
@patch("mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.get_detector_type")
@patch("mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.logger")
def test_initialise_extruder(fake_log, fake_det, fake_caput, fake_caget):
    fake_caget.return_value = "/path/to/visit"
    fake_det.return_value = Eiger()
    initialise_extruderi24()
    assert fake_caput.call_count == 10
    assert fake_caget.call_count == 1


@patch("mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.caput")
@patch("mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.get_detector_type")
def test_moveto_enterhutch(fake_det, fake_caput, dummy_parser):
    fake_args = dummy_parser.parse_args(["enterhutch"])
    fake_det.return_value = Eiger()
    moveto(fake_args)
    assert fake_caput.call_count == 1


@patch("mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.caput")
@patch("mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.get_detector_type")
def test_moveto_laseron_for_eiger(fake_det, fake_caput, dummy_parser):
    fake_det.return_value = Eiger()
    fake_args = dummy_parser.parse_args(["laseron"])
    moveto(fake_args)
    assert fake_caput.call_count == 2


@patch("mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.caput")
@patch("mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.get_detector_type")
def test_moveto_laseroff_for_pilatus(fake_det, fake_caput, dummy_parser):
    fake_det.return_value = Pilatus()
    fake_args = dummy_parser.parse_args(["laseroff"])
    moveto(fake_args)
    assert fake_caput.call_count == 2


@patch(
    "mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.open",
    mock_open(read_data=params_file_str),
)
@patch("mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.DCID")
@patch("mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.call_nexgen")
@patch("mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.caput")
@patch("mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.caget")
@patch("mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.sup")
@patch("mx_bluesky.I24.serial.extruder.i24ssx_Extruder_Collect_py3v2.get_detector_type")
def test_run_extruder_with_eiger(
    fake_det, fake_sup, fake_caget, fake_caput, fake_nexgen, fake_dcid
):
    fake_det.return_value = Eiger()
    run_extruderi24()
    assert fake_nexgen.call_count == 1
    assert fake_dcid.call_count == 1
    # Check temporary piilatus hack is in there
    assert fake_sup.pilatus.call_count == 2
