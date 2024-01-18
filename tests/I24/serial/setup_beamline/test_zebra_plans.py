from functools import partial
from unittest.mock import MagicMock

from dodal.devices.zebra import SOFT_IN2, Zebra
from ophyd.status import Status

from mx_bluesky.I24.serial.setup_beamline.setup_zebra_plans import (
    arm_zebra,
    disarm_zebra,
    setup_zebra_for_quickshot_plan,
)


def test_arm_and_disarm_zebra(zebra: Zebra, RE):
    zebra.pc.arm.TIMEOUT = 0.5

    def side_effect(set_armed: int, _):
        zebra.pc.arm.armed.set(set_armed)
        return Status(done=True, success=True)

    mock_arm = MagicMock(side_effect=partial(side_effect, 1))

    zebra.pc.arm.arm_set.set = mock_arm

    zebra.pc.arm.armed.set(0)
    RE(arm_zebra(zebra))
    assert zebra.pc.is_armed()

    mock_disarm = MagicMock(side_effect=partial(side_effect, 0))

    zebra.pc.arm.disarm_set.set = mock_disarm

    zebra.pc.arm.armed.set(1)
    RE(disarm_zebra(zebra))
    assert not zebra.pc.is_armed()


def test_setup_zebra_for_quickshot(zebra: Zebra, RE):
    RE(
        setup_zebra_for_quickshot_plan(
            zebra, gate_start=1.0, gate_width=0.01, wait=True
        )
    )
    assert zebra.pc.arm_source.get() == "Soft"
    assert zebra.pc.gate_start.get() == 1.0
    assert zebra.pc.gate_input.get() == SOFT_IN2


def test_setup_zebra_for_extruder_pp_collection_with_eiger(zebra: Zebra, RE):
    pass
