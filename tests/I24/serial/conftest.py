import pytest
from bluesky.run_engine import RunEngine
from dodal.beamlines import i24
from dodal.devices.zebra import Zebra


@pytest.fixture
def zebra() -> Zebra:
    return i24.zebra(fake_with_ophyd_sim=True)


@pytest.fixture
def RE():
    return RunEngine()
