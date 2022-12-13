from bluesky.plan_stubs import read
from ophyd import Component, Device, EpicsSignal


class Undulator(Device):
    id_gap_pv = "SR04J-MO-SERVC-01:CURRGAPD"
    id_gap: EpicsSignal = Component(EpicsSignal, id_gap_pv)

    def read_gap_mm(self):
        yield from read(Undulator.id_gap)


class UndulatorMonitor:
    gap_equality_threshold = 5.0e-4

    def __init__(self, device: Undulator, nominal_gap=8.362):
        self.undulator = device
        self.nominal_gap_mm: float = nominal_gap

    def _is_nominal(self, present_gap_mm):
        delta = abs(present_gap_mm - self.nominal_gap_mm)
        return delta < UndulatorMonitor.gap_equality_threshold

    def is_gap_at_nominal_value(self):
        present_gap = yield from self.undulator.read_gap_mm()
        yield self._is_nominal(present_gap)
