from mx_bluesky.hdm.nominal_min_max import NominalMinMax, SymmetricNominalMinMax
from mx_bluesky.hdm.temperature_specific_pair import TemperatureSpecificPair


class LookUp:
    def __init__(self):
        self.current_look_up: set[NominalMinMax] = {
            SymmetricNominalMinMax(233, 10),
            SymmetricNominalMinMax(300, 10),
            SymmetricNominalMinMax(135, 10),
        }

        self.gap_look_up: set[NominalMinMax] = {NominalMinMax(12.22, 12.2, 12.3)}

        self.temperature_look_up: set[TemperatureSpecificPair] = {
            TemperatureSpecificPair(37.0, 12.22, 233),
            TemperatureSpecificPair(40.0, 12.22, 300),
        }

    def get_nominal_current(self, ring_current: float):
        for current in self.current_look_up:
            nominal = current.get_nominal_if_in_range(ring_current)
            if nominal is not None:
                return nominal

    def get_nominal_gap(self, undulator_gap: float):
        for gap in self.gap_look_up:
            nominal = gap.get_nominal_if_in_range(undulator_gap)
            if nominal is not None:
                return nominal
