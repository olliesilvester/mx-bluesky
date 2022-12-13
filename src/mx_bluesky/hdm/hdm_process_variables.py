class FilterPvSuffices:
    def __init__(self):
        self.y_filter_prefix = "MO-FLTR-01:Y"
        self.filter_position_selection_suffix = ":MP:SELECT"
        self.filter_position_suffix = ":P:UPD.D"
        self.filter_in_place_suffix = ":MP:INPOSe"

    def __build_suffix_using(self, final_suffix):
        return _combine(self.y_filter_prefix, final_suffix)

    def getFilterPositionSelectionSuffix(self):
        return self.__build_suffix_using(self.filter_position_selection_suffix)

    def getFilterPositionSuffix(self):
        return self.__build_suffix_using(self.filter_position_suffix)

    def getFilterInPlaceSuffix(self):
        return self.__build_suffix_using(self.filter_in_place_suffix)


def _combine(prefix, suffix):
    return "%s%s" % (prefix, suffix)


"""
class HdmProcessVariables(beamline="BL04J"):
    def __init__(self):
        self.beamline_prefix = _combine(beamline, "-")
        self.filter_in_place = _combine(
            self.beamline_prefix,
        )
"""
