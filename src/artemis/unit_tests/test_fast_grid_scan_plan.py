import types
from unittest.mock import ANY, MagicMock, patch

import bluesky.plan_stubs as bps
import pytest
from bluesky.callbacks import CallbackBase
from bluesky.run_engine import RunEngine
from ophyd.sim import make_fake_device

from artemis.devices.det_dim_constants import (
    EIGER2_X_4M_DIMENSION,
    EIGER_TYPE_EIGER2_X_4M,
    EIGER_TYPE_EIGER2_X_16M,
)
from artemis.devices.eiger import EigerDetector
from artemis.devices.fast_grid_scan import FastGridScan
from artemis.devices.fast_grid_scan_composite import FGSComposite
from artemis.devices.slit_gaps import SlitGaps
from artemis.devices.synchrotron import Synchrotron
from artemis.devices.undulator import Undulator
from artemis.exceptions import WarningException
from artemis.experiment_plans.fast_grid_scan_plan import (
    read_hardware_for_ispyb,
    run_gridscan,
    run_gridscan_and_move,
    wait_for_fgs_valid,
)
from artemis.external_interaction.callbacks import (
    FGSCallbackCollection,
    VerbosePlanExecutionLoggingCallback,
)
from artemis.log import set_up_logging_handlers
from artemis.parameters import FullParameters
from artemis.utils import Point3D


def test_given_full_parameters_dict_when_detector_name_used_and_converted_then_detector_constants_correct():
    params = FullParameters().to_dict()
    assert (
        params["detector_params"]["detector_size_constants"] == EIGER_TYPE_EIGER2_X_16M
    )
    params["detector_params"]["detector_size_constants"] = EIGER_TYPE_EIGER2_X_4M
    params: FullParameters = FullParameters.from_dict(params)
    det_dimension = params.detector_params.detector_size_constants.det_dimension
    assert det_dimension == EIGER2_X_4M_DIMENSION


def test_when_run_gridscan_called_then_generator_returned():
    plan = run_gridscan(MagicMock(), MagicMock())
    assert isinstance(plan, types.GeneratorType)


def test_read_hardware_for_ispyb_updates_from_ophyd_devices():
    RE = RunEngine({})
    params = FullParameters()

    undulator_test_value = 1.234
    FakeUndulator = make_fake_device(Undulator)
    undulator: Undulator = FakeUndulator(name="undulator")
    undulator.gap.user_readback.sim_put(undulator_test_value)

    synchrotron_test_value = "test"
    FakeSynchrotron = make_fake_device(Synchrotron)
    synchrotron: Synchrotron = FakeSynchrotron(name="synchrotron")
    synchrotron.machine_status.synchrotron_mode.sim_put(synchrotron_test_value)

    xgap_test_value = 0.1234
    ygap_test_value = 0.2345
    FakeSlitGaps = make_fake_device(SlitGaps)
    slit_gaps: SlitGaps = FakeSlitGaps(name="slit_gaps")
    slit_gaps.xgap.sim_put(xgap_test_value)
    slit_gaps.ygap.sim_put(ygap_test_value)

    class TestCB(CallbackBase):
        params = FullParameters()

        def event(self, doc: dict):
            params.ispyb_params.undulator_gap = doc["data"]["undulator_gap"]
            params.ispyb_params.synchrotron_mode = doc["data"][
                "synchrotron_machine_status_synchrotron_mode"
            ]
            params.ispyb_params.slit_gap_size_x = doc["data"]["slit_gaps_xgap"]
            params.ispyb_params.slit_gap_size_y = doc["data"]["slit_gaps_ygap"]

    testcb = TestCB()
    testcb.params = params
    RE.subscribe(testcb)

    def standalone_read_hardware_for_ispyb(und, syn, slits):
        yield from bps.open_run()
        yield from read_hardware_for_ispyb(und, syn, slits)
        yield from bps.close_run()

    RE(standalone_read_hardware_for_ispyb(undulator, synchrotron, slit_gaps))
    params = testcb.params

    assert params.ispyb_params.undulator_gap == undulator_test_value
    assert params.ispyb_params.synchrotron_mode == synchrotron_test_value
    assert params.ispyb_params.slit_gap_size_x == xgap_test_value
    assert params.ispyb_params.slit_gap_size_y == ygap_test_value


@patch("artemis.experiment_plans.fast_grid_scan_plan.run_gridscan")
@patch("artemis.experiment_plans.fast_grid_scan_plan.move_xyz")
def test_results_adjusted_and_passed_to_move_xyz(
    move_xyz: MagicMock, run_gridscan: MagicMock
):
    RE = RunEngine({})
    set_up_logging_handlers(logging_level="INFO", dev_mode=True)
    RE.subscribe(VerbosePlanExecutionLoggingCallback())
    params = FullParameters()
    subscriptions = FGSCallbackCollection.from_params(params)

    subscriptions.zocalo_handler.zocalo_interactor.wait_for_result = MagicMock()
    subscriptions.zocalo_handler.zocalo_interactor.run_end = MagicMock()
    subscriptions.zocalo_handler.zocalo_interactor.run_start = MagicMock()
    subscriptions.zocalo_handler.zocalo_interactor.wait_for_result.return_value = (
        Point3D(1, 2, 3)
    )

    motor_position = params.grid_scan_params.grid_position_to_motor_position(
        Point3D(0.5, 1.5, 2.5)
    )
    FakeComposite: FGSComposite = make_fake_device(FGSComposite)
    FakeEiger: EigerDetector = make_fake_device(EigerDetector)
    RE(
        run_gridscan_and_move(
            FakeComposite("test", name="fgs"),
            FakeEiger.with_params(params=params.detector_params, name="test"),
            params,
            subscriptions,
        )
    )
    move_xyz.assert_called_once_with(ANY, motor_position)


@patch("bluesky.plan_stubs.mv")
def test_results_passed_to_move_motors(bps_mv: MagicMock):
    from artemis.experiment_plans.fast_grid_scan_plan import move_xyz

    RE = RunEngine({})
    set_up_logging_handlers(logging_level="INFO", dev_mode=True)
    RE.subscribe(VerbosePlanExecutionLoggingCallback())
    params = FullParameters()
    motor_position = params.grid_scan_params.grid_position_to_motor_position(
        Point3D(1, 2, 3)
    )
    FakeComposite = make_fake_device(FGSComposite)
    RE(move_xyz(FakeComposite("test", name="fgs").sample_motors, motor_position))
    bps_mv.assert_called_once_with(
        ANY, motor_position.x, ANY, motor_position.y, ANY, motor_position.z
    )


@patch("artemis.experiment_plans.fast_grid_scan_plan.run_gridscan.do_fgs")
@patch("artemis.experiment_plans.fast_grid_scan_plan.run_gridscan")
@patch("artemis.experiment_plans.fast_grid_scan_plan.move_xyz")
def test_individual_plans_triggered_once_and_only_once_in_composite_run(
    move_xyz: MagicMock,
    run_gridscan: MagicMock,
    do_fgs: MagicMock,
):
    RE = RunEngine({})
    set_up_logging_handlers(logging_level="INFO", dev_mode=True)
    RE.subscribe(VerbosePlanExecutionLoggingCallback())
    params = FullParameters()

    subscriptions = FGSCallbackCollection.from_params(params)
    subscriptions.zocalo_handler.zocalo_interactor.wait_for_result = MagicMock()
    subscriptions.zocalo_handler.zocalo_interactor.run_end = MagicMock()
    subscriptions.zocalo_handler.zocalo_interactor.run_start = MagicMock()
    subscriptions.zocalo_handler.zocalo_interactor.wait_for_result.return_value = (
        Point3D(1, 2, 3)
    )

    FakeComposite: FGSComposite = make_fake_device(FGSComposite)
    FakeEiger: EigerDetector = make_fake_device(EigerDetector)
    fake_composite = FakeComposite("test", name="fakecomposite")
    fake_eiger = (FakeEiger.with_params(params=params.detector_params, name="test"),)
    RE(
        run_gridscan_and_move(
            fake_composite,
            fake_eiger,
            params,
            subscriptions,
        )
    )

    run_gridscan.assert_called_once_with(fake_composite, fake_eiger, params)
    move_xyz.assert_called_once_with(ANY, Point3D(0.05, 0.15000000000000002, 0.25))


@patch("artemis.experiment_plans.fast_grid_scan_plan.run_gridscan.do_fgs")
@patch("artemis.experiment_plans.fast_grid_scan_plan.run_gridscan")
@patch("artemis.experiment_plans.fast_grid_scan_plan.move_xyz")
def test_logging_within_plan(
    move_xyz: MagicMock,
    run_gridscan: MagicMock,
    do_fgs: MagicMock,
):
    RE = RunEngine({})
    set_up_logging_handlers(logging_level="INFO", dev_mode=True)
    RE.subscribe(VerbosePlanExecutionLoggingCallback())
    params = FullParameters()

    subscriptions = FGSCallbackCollection.from_params(params)
    subscriptions.zocalo_handler.zocalo_interactor.wait_for_result = MagicMock()
    subscriptions.zocalo_handler.zocalo_interactor.run_end = MagicMock()
    subscriptions.zocalo_handler.zocalo_interactor.run_start = MagicMock()
    subscriptions.zocalo_handler.zocalo_interactor.wait_for_result.return_value = (
        Point3D(1, 2, 3)
    )

    FakeComposite = make_fake_device(FGSComposite)
    FakeEiger: EigerDetector = make_fake_device(EigerDetector)
    fake_composite = FakeComposite("test", name="fakecomposite")
    fake_eiger = FakeEiger.with_params(params=params.detector_params, name="test")

    RE(
        run_gridscan_and_move(
            fake_composite,
            fake_eiger,
            params,
            subscriptions,
        )
    )
    # RE(bps.close_run())

    run_gridscan.assert_called_once_with(fake_composite, fake_eiger, params)
    move_xyz.assert_called_once_with(ANY, Point3D(0.05, 0.15000000000000002, 0.25))


@patch("artemis.experiment_plans.fast_grid_scan_plan.bps.sleep")
def test_GIVEN_scan_already_valid_THEN_wait_for_FGS_returns_immediately(
    patch_sleep: MagicMock,
):
    test_fgs: FastGridScan = make_fake_device(FastGridScan)("prefix", name="fake_fgs")

    test_fgs.scan_invalid.sim_put(False)
    test_fgs.position_counter.sim_put(0)

    RE = RunEngine({})

    RE(wait_for_fgs_valid(test_fgs))

    patch_sleep.assert_not_called()


@patch("artemis.experiment_plans.fast_grid_scan_plan.bps.sleep")
def test_GIVEN_scan_not_valid_THEN_wait_for_FGS_raises_and_sleeps_called(
    patch_sleep: MagicMock,
):
    test_fgs: FastGridScan = make_fake_device(FastGridScan)("prefix", name="fake_fgs")

    test_fgs.scan_invalid.sim_put(True)
    test_fgs.position_counter.sim_put(0)

    RE = RunEngine({})
    with pytest.raises(WarningException):
        RE(wait_for_fgs_valid(test_fgs))

    patch_sleep.assert_called()
