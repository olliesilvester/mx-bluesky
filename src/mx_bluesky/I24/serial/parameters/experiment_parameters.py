from pydantic import BaseModel

from mx_bluesky.I24.serial.fixed_target.ft_utils import (
    ChipType,
    MappingType,
    PumpProbeSetting,
)


class SerialExptParameters(BaseModel):
    visit: str
    directory: str
    filename: str
    exposure_time_s: float
    detector_distance_mm: float
    detector_type: str
    pump_status: bool


class ExtruderParameters(SerialExptParameters):
    num_images: int
    pump_exposure_s: float
    pump_delay_s: float


class FixedTargetParameters(SerialExptParameters):
    chip_type: ChipType
    map_type: MappingType
    pump_repeat: PumpProbeSetting
