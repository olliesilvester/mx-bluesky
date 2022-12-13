from bluesky.plan_stubs import read
from ophyd import Component, Device, EpicsSignal


class Filters(Device):
    selection_sig: EpicsSignal = Component(EpicsSignal, "BL04J-M0-FLTR")
