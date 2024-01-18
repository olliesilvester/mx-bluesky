from functools import partial
from unittest.mock import MagicMock

import pytest
from bluesky.run_engine import RunEngine
from dodal.beamlines import i24
from dodal.devices.zebra import Zebra
from ophyd.status import Status

from mx_bluesky.I24.serial.setup_beamline.zebra_plans import arm_zebra, disarm_zebra


@pytest.fixture
def zebra() -> Zebra:
    return i24.zebra(fake_with_ophyd_sim=True)


def test_arm_and_disarm_zebra(zebra: Zebra):
    RE = RunEngine()

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
