import pytest
from bluesky.run_engine import RunEngine
from dodal.beamlines import i24
from dodal.devices.oav.oav_detector import OAV
from dodal.devices.oav.oav_parameters import OAVParameters

from mx_bluesky.I24.serial.fixed_target.i24ssx_moveonclick import (
    _get_beam_centre,
    _read_zoom_level,
)


@pytest.fixture
def fake_oav() -> OAV:
    return i24.oav(fake_with_ophyd_sim=True)


@pytest.fixture
def mock_oavparams(dummy_jCameraSettings, dummy_oav_config, dummy_display_config):
    fake_config = {
        "zoom_params_file": dummy_jCameraSettings.name,
        "oav_config_json": dummy_oav_config.name,
        "display_config": dummy_display_config.name,
    }
    return OAVParameters("xrayCentring", **fake_config)


def test_read_zoom_level(fake_oav):
    fake_oav.zoom_controller.level.sim_put("3.0")
    RE = RunEngine(call_returns_result=True)
    zoom_level = RE(_read_zoom_level(fake_oav)).plan_result
    assert zoom_level == 3.0


@pytest.mark.parametrize(
    "zoom_level, expected_beamX, expected_beamY",
    [("1.0", 475, 309), ("2.0", 638, 392), ("3.0", 638, 392)],
)
def test_get_beam_centre(
    zoom_level,
    expected_beamX,
    expected_beamY,
    fake_oav: OAV,
    mock_oavparams: OAVParameters,
):
    fake_oav.zoom_controller.level.sim_put(zoom_level)
    beamX, beamY = _get_beam_centre(fake_oav, mock_oavparams)
    assert beamX == expected_beamX
    assert beamY == expected_beamY
