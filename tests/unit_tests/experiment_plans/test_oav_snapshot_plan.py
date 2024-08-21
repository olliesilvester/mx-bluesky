import dataclasses
from datetime import datetime
from unittest.mock import patch

import pytest
from bluesky.simulators import assert_message_and_return_remaining
from dodal.devices.aperturescatterguard import ApertureScatterguard
from dodal.devices.backlight import Backlight
from dodal.devices.oav.oav_detector import OAV
from dodal.devices.oav.oav_parameters import OAVParameters
from dodal.devices.oav.utils import ColorMode
from dodal.devices.smargon import Smargon

from hyperion.experiment_plans.oav_snapshot_plan import (
    OAV_SNAPSHOT_SETUP_SHOT,
    OavSnapshotComposite,
    oav_snapshot_plan,
)
from hyperion.parameters.components import WithSnapshot
from hyperion.parameters.constants import DocDescriptorNames

from ...conftest import raw_params_from_file


@pytest.fixture
def oav_snapshot_params():
    return WithSnapshot(
        **raw_params_from_file(
            "tests/test_data/parameter_json_files/test_oav_snapshot_params.json"
        )
    )


@dataclasses.dataclass
class CompositeImpl(OavSnapshotComposite):
    smargon: Smargon
    oav: OAV
    aperture_scatterguard: ApertureScatterguard
    backlight: Backlight


@pytest.fixture
def oav_snapshot_composite(smargon, oav, aperture_scatterguard, backlight):
    oav.zoom_controller.fvst.sim_put("5.0x")
    return CompositeImpl(
        smargon=smargon,
        oav=oav,
        aperture_scatterguard=aperture_scatterguard,
        backlight=backlight,
    )


@patch("hyperion.experiment_plans.oav_snapshot_plan.datetime", spec=datetime)
def test_oav_snapshot_plan_issues_rotations_and_generates_events(
    mock_datetime, oav_snapshot_params, oav_snapshot_composite, sim_run_engine
):
    mock_datetime.now.return_value = datetime.fromisoformat("2024-06-07T10:06:23")
    msgs = sim_run_engine.simulate_plan(
        oav_snapshot_plan(
            oav_snapshot_composite,
            oav_snapshot_params,
            OAVParameters(oav_config_json="tests/test_data/test_OAVCentring.json"),
        )
    )

    msgs = assert_message_and_return_remaining(
        msgs,
        lambda msg: msg.command == "set"
        and msg.obj.name == "oav_cam_color_mode"
        and msg.args[0] == ColorMode.RGB1,
    )
    msgs = assert_message_and_return_remaining(
        msgs,
        lambda msg: msg.command == "set"
        and msg.obj.name == "oav_cam_acquire_period"
        and msg.args[0] == 0.05,
    )
    msgs = assert_message_and_return_remaining(
        msgs,
        lambda msg: msg.command == "set"
        and msg.obj.name == "oav_cam_acquire_time"
        and msg.args[0] == 0.075,
    )
    msgs = assert_message_and_return_remaining(
        msgs,
        lambda msg: msg.command == "set"
        and msg.obj.name == "oav_cam_gain"
        and msg.args[0] == 1,
    )
    msgs = assert_message_and_return_remaining(
        msgs,
        lambda msg: msg.command == "set"
        and msg.obj.name == "oav_zoom_controller"
        and msg.args[0] == "5.0x",
    )
    msgs = assert_message_and_return_remaining(
        msgs,
        lambda msg: msg.command == "set"
        and msg.obj.name == "oav_snapshot_directory"
        and msg.args[0] == "/tmp/my_snapshots",
    )
    for expected in [
        {"omega": 0, "filename": "100623_oav_snapshot_0"},
        {"omega": 90, "filename": "100623_oav_snapshot_90"},
        {"omega": 180, "filename": "100623_oav_snapshot_180"},
        {"omega": 270, "filename": "100623_oav_snapshot_270"},
    ]:
        msgs = assert_message_and_return_remaining(
            msgs,
            lambda msg: msg.command == "set"
            and msg.obj.name == "smargon-omega"
            and msg.args[0] == expected["omega"]
            and msg.kwargs["group"] == OAV_SNAPSHOT_SETUP_SHOT,
        )
        msgs = assert_message_and_return_remaining(
            msgs,
            lambda msg: msg.command == "set"
            and msg.obj.name == "oav_snapshot_filename"
            and msg.args[0] == expected["filename"],
        )
        msgs = assert_message_and_return_remaining(
            msgs,
            lambda msg: msg.command == "trigger"
            and msg.obj.name == "oav_snapshot"
            and msg.kwargs["group"] is None,
        )
        msgs = assert_message_and_return_remaining(
            msgs,
            lambda msg: msg.command == "wait" and msg.kwargs["group"] is None,
        )
        msgs = assert_message_and_return_remaining(
            msgs,
            lambda msg: msg.command == "create"
            and msg.kwargs["name"]
            == DocDescriptorNames.OAV_ROTATION_SNAPSHOT_TRIGGERED,
        )
        msgs = assert_message_and_return_remaining(
            msgs, lambda msg: msg.command == "read" and msg.obj.name == "oav_snapshot"
        )
        msgs = assert_message_and_return_remaining(
            msgs, lambda msg: msg.command == "save"
        )
