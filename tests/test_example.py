from unittest.mock import patch

from bluesky import RunEngine
from ophyd.sim import make_fake_device

# from mx_bluesky.hdm.hdm_warming import Synchrotron, test_plan

"""
@patch("mx_bluesky.example.print")
def test_example_reads_correct_value(mock_print):
    fake_device: Synchrotron = make_fake_device(Synchrotron)(name="fake_synch")
    fake_device.ring_current.sim_put(378.8)
    RE = RunEngine()
    RE(test_plan(fake_device))

    assert mock_print.called_once_with(str(378.8))
"""
