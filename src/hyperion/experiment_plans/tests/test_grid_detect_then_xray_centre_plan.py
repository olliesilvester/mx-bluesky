from typing import Any, Dict, Generator
from unittest.mock import ANY, MagicMock, patch

import pytest
from bluesky.run_engine import RunEngine
from dodal.beamlines.i03 import detector_motion
from dodal.devices.backlight import Backlight
from dodal.devices.eiger import EigerDetector
from dodal.devices.oav.oav_parameters import OAVParameters
from numpy.testing import assert_array_equal

from hyperion.experiment_plans.grid_detect_then_xray_centre_plan import (
    GridDetectThenXRayCentreComposite,
    detect_grid_and_do_gridscan,
    grid_detect_then_xray_centre,
    wait_for_det_to_finish_moving,
)
from hyperion.external_interaction.callbacks.oav_snapshot_callback import (
    OavSnapshotCallback,
)
from hyperion.parameters.plan_specific.grid_scan_with_edge_detect_params import (
    GridScanWithEdgeDetectInternalParameters,
)
from hyperion.parameters.plan_specific.gridscan_internal_params import (
    GridscanInternalParameters,
)


def _fake_grid_detection(
    devices: Any,
    parameters: OAVParameters,
    out_parameters,
    snapshot_template: str,
    snapshot_dir: str,
    grid_width_microns: float = 0,
    box_size_um: float = 0.0,
):
    out_parameters.x_start = 0
    out_parameters.y1_start = 0
    out_parameters.y2_start = 0
    out_parameters.z1_start = 0
    out_parameters.z2_start = 0
    out_parameters.x_steps = 10
    out_parameters.y_steps = 2
    out_parameters.z_steps = 2
    out_parameters.x_step_size = 1
    out_parameters.y_step_size = 1
    out_parameters.z_step_size = 1
    return []


@pytest.fixture
def grid_detect_devices(aperture_scatterguard, backlight, detector_motion):
    return GridDetectThenXRayCentreComposite(
        aperture_scatterguard=aperture_scatterguard,
        attenuator=MagicMock(),
        backlight=backlight,
        detector_motion=detector_motion,
        eiger=MagicMock(),
        fast_grid_scan=MagicMock(),
        flux=MagicMock(),
        oav=MagicMock(),
        smargon=MagicMock(),
        synchrotron=MagicMock(),
        s4_slit_gaps=MagicMock(),
        undulator=MagicMock(),
        zebra=MagicMock(),
    )


def test_wait_for_detector(RE):
    d_m = detector_motion(fake_with_ophyd_sim=True)
    with pytest.raises(TimeoutError):
        RE(wait_for_det_to_finish_moving(d_m, 0.2))
    d_m.shutter.sim_put(1)  # type: ignore
    d_m.z.motor_done_move.sim_put(1)  # type: ignore
    RE(wait_for_det_to_finish_moving(d_m, 0.5))


def test_full_grid_scan(test_fgs_params, test_config_files):
    devices = MagicMock()
    plan = grid_detect_then_xray_centre(devices, test_fgs_params, test_config_files)
    assert isinstance(plan, Generator)


@patch(
    "hyperion.experiment_plans.grid_detect_then_xray_centre_plan.wait_for_det_to_finish_moving",
    autospec=True,
)
@patch(
    "hyperion.experiment_plans.grid_detect_then_xray_centre_plan.grid_detection_plan",
    autospec=True,
)
@patch(
    "hyperion.experiment_plans.grid_detect_then_xray_centre_plan.flyscan_xray_centre",
    autospec=True,
)
@patch(
    "hyperion.experiment_plans.grid_detect_then_xray_centre_plan.OavSnapshotCallback",
    autospec=True,
)
def test_detect_grid_and_do_gridscan(
    mock_oav_callback_init: MagicMock,
    mock_flyscan_xray_centre_plan: MagicMock,
    mock_grid_detection_plan: MagicMock,
    mock_wait_for_detector: MagicMock,
    grid_detect_devices: GridDetectThenXRayCentreComposite,
    RE: RunEngine,
    test_full_grid_scan_params: GridScanWithEdgeDetectInternalParameters,
    test_config_files: Dict,
):
    mock_oav_callback = OavSnapshotCallback()
    mock_oav_callback.out_upper_left = [[0, 1], [2, 3]]
    mock_oav_callback.snapshot_filenames = [["test"], ["test3"]]
    mock_oav_callback_init.return_value = mock_oav_callback
    mock_grid_detection_plan.side_effect = _fake_grid_detection
    assert grid_detect_devices.aperture_scatterguard.aperture_positions is not None

    with patch.object(
        grid_detect_devices.aperture_scatterguard, "set", MagicMock()
    ) as mock_aperture_scatterguard:
        RE(
            detect_grid_and_do_gridscan(
                grid_detect_devices,
                parameters=test_full_grid_scan_params,
                oav_params=OAVParameters("xrayCentring", **test_config_files),
            )
        )
        # Verify we called the grid detection plan
        mock_grid_detection_plan.assert_called_once()

        # Verify callback to oav snaposhot was called
        mock_oav_callback_init.assert_called_once()

        # Check backlight was moved OUT
        assert grid_detect_devices.backlight.pos.get() == Backlight.OUT

        # Check aperture was changed to SMALL
        mock_aperture_scatterguard.assert_called_once_with(
            grid_detect_devices.aperture_scatterguard.aperture_positions.SMALL
        )

        # Check we wait for detector to finish moving
        mock_wait_for_detector.assert_called_once()

        # Check we called out to underlying fast grid scan plan
        mock_flyscan_xray_centre_plan.assert_called_once_with(ANY, ANY)


@patch(
    "hyperion.experiment_plans.grid_detect_then_xray_centre_plan.wait_for_det_to_finish_moving",
    autospec=True,
)
@patch(
    "hyperion.experiment_plans.grid_detect_then_xray_centre_plan.grid_detection_plan",
    autospec=True,
)
@patch(
    "hyperion.experiment_plans.grid_detect_then_xray_centre_plan.flyscan_xray_centre",
    autospec=True,
)
@patch(
    "hyperion.experiment_plans.grid_detect_then_xray_centre_plan.OavSnapshotCallback",
    autospec=True,
)
def test_when_full_grid_scan_run_then_parameters_sent_to_fgs_as_expected(
    mock_oav_callback_init: MagicMock,
    mock_flyscan_xray_centre_plan: MagicMock,
    mock_grid_detection_plan: MagicMock,
    _: MagicMock,
    eiger: EigerDetector,
    grid_detect_devices: GridDetectThenXRayCentreComposite,
    RE: RunEngine,
    test_full_grid_scan_params: GridScanWithEdgeDetectInternalParameters,
    test_config_files: Dict,
):
    mock_oav_callback = OavSnapshotCallback()
    mock_oav_callback.snapshot_filenames = [["a", "b", "c"], ["d", "e", "f"]]
    mock_oav_callback.out_upper_left = [[1, 2], [1, 3]]

    mock_oav_callback_init.return_value = mock_oav_callback

    mock_grid_detection_plan.side_effect = _fake_grid_detection

    with patch.object(eiger.do_arm, "set", MagicMock()), patch.object(
        grid_detect_devices.aperture_scatterguard, "set", MagicMock()
    ):
        RE(
            detect_grid_and_do_gridscan(
                grid_detect_devices,
                parameters=test_full_grid_scan_params,
                oav_params=OAVParameters("xrayCentring", **test_config_files),
            )
        )

        params: GridscanInternalParameters = mock_flyscan_xray_centre_plan.call_args[0][
            1
        ]

        assert isinstance(params, GridscanInternalParameters)

        ispyb_params = params.hyperion_params.ispyb_params
        assert_array_equal(ispyb_params.upper_left, [1, 2, 3])
        assert ispyb_params.xtal_snapshots_omega_start == [
            "c",
            "b",
            "a",
        ]
        assert ispyb_params.xtal_snapshots_omega_end == [
            "f",
            "e",
            "d",
        ]

        assert params.hyperion_params.detector_params.num_triggers == 40

        assert params.experiment_params.x_axis.full_steps == 10
        assert params.experiment_params.y_axis.end == 1

        # Parameters can be serialized
        params.json()
