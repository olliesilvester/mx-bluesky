from unittest.mock import MagicMock

import pytest
from bluesky.run_engine import RunEngine
from dodal.beamlines import i24
from dodal.devices.zebra import Zebra
from ophyd.status import Status


@pytest.fixture
def zebra() -> Zebra:
    zebra = i24.zebra(fake_with_ophyd_sim=True)
    mock_arm_disarm = MagicMock(
        side_effect=zebra.pc.arm.armed.set,
        return_value=Status(done=True, success=True),
    )
    zebra.pc.arm.set = mock_arm_disarm
    return zebra


@pytest.fixture
def RE():
    return RunEngine()
