from bluesky.plan_stubs import read
from ophyd import Component, Device, EpicsSignal


class Synchrotron(Device):
    ring_current_sig: EpicsSignal = Component(EpicsSignal, "SR-DI-DCCT-01:SIGNAL")

