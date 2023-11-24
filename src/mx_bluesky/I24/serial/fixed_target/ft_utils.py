from enum import IntEnum


class MappingType(IntEnum):
    NoMap = 0
    Lite = 1
    Full = 2


class ChipType(IntEnum):
    Oxford = 0
    OxfordInner = 1
    Custom = 2
    Minichip = 3  # Mini oxford, 1 city block only


class PumpProbeSetting(IntEnum):
    NoPP = 0
    Short1 = 1
    Short2 = 2
    Repeat1 = 3
    Repeat2 = 4
    Repeat3 = 5
    Repeat5 = 6
    Repeat10 = 7
