class TemperatureSpecificPair:
    def __init__(
        self, temperature: float, gap: float, current: float, tolerance: float = 0.1
    ):
        self.specific_t = temperature
        self.gap = gap
        self.current = current
        self.tolerance = abs(tolerance)

    def _is_within_tolerance(self, temperature: float):
        return abs(temperature - self.specific_t) < self.tolerance

    def get_gap_and_current(self, temperature: float):
        if not self._is_within_tolerance(temperature):
            return None, None
        return self.gap, self.current
