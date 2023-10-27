from typing import Dict

# from unittest.mock import patch
import pytest
from dodal.beamlines import i24
from dodal.devices.oav.oav_detector import OAV

from mx_bluesky.I24.serial.fixed_target.i24ssx_moveonclick import get_beam_centre

# @patch("mx_bluesky.I24.serial.fixed_target.i24ssx_moveonclick.caput")
# def test_onMouse(fake_caput):
#    with patch("mx_bluesky.I24.serial.fixed_target.i24ssx_moveonclick.cv"):
#        onMouse(4, 0, 0, "", "")
#    assert fake_caput.call_count == 2


@pytest.fixture
def fake_oav() -> OAV:
    return i24.oav(fake_with_ophyd_sim=True)


@pytest.fixture
def mock_oavconfig(dummy_jCameraSettings, dummy_oav_config, dummy_display_config):
    return {
        "zoom_params_file": dummy_jCameraSettings.name,
        "oav_config_json": dummy_oav_config.name,
        "display_config": dummy_display_config.name,
    }


# FIXME Does't work for 1.0, not sure what's wronge but I think something
# on how zoom is set in oav_params
@pytest.mark.parametrize(
    "zoom_level, expected_beamX, expected_beamY",
    [("1.0", 475, 309), ("2.0", 638, 392), ("3.0", 638, 392)],
)
def test_get_beam_centre(
    zoom_level,
    expected_beamX,
    expected_beamY,
    fake_oav: OAV,
    mock_oavconfig: Dict,
):
    fake_oav.zoom_controller.level.sim_put(zoom_level)
    beamX, beamY = get_beam_centre(fake_oav, mock_oavconfig)
    assert beamX == expected_beamX
    assert beamY == expected_beamY
