class NominalMinMax:
    def __init__(self, nominal: float, minimum: float, maximum: float):
        self.nominal = nominal
        if minimum > maximum:
            raise TypeError("Minimum is greater than Maximum")
        self.minimum = minimum
        self.maximum = maximum
        if self.get_nominal_if_in_range(nominal) is None:
            raise TypeError("Nominal value is not within min-max range")

    def get_nominal_if_in_range(self, value: float):
        if self.minimum > value or self.maximum < value:
            return None
        else:
            return self.nominal


class SymmetricNominalMinMax(NominalMinMax):
    def __init__(self, nominal: float, half_width: float):
        abs_half_width: float = abs(half_width)
        super().__init__(nominal, nominal - abs_half_width, nominal + abs_half_width)
