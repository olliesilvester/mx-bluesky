from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional, Union

from dataclasses_json import DataClassJsonMixin
from pydantic import BaseModel, ConfigDict
from pydantic.dataclasses import dataclass


@dataclass(config=ConfigDict(validate_assignment=True))
class GeneralParameters(DataClassJsonMixin):
    visit: Union[Path, str]
    directory: Union[Path, str]
    filename: str
    exp_time: float
    det_type: str
    det_dist: float

    def __post_init__(self):
        if not isinstance(self.visit, Path):
            self.visit = Path(self.visit)
        if self.det_type == "pilatus":
            # Pilatus hack.
            # If filename ends in a digit this causes processing/pilatus pain.
            m = re.search(r"\d+$", self.filename)
            if m is not None:
                self.filename = self.filename + "-"

    @property
    def collection_path(self):
        return self.visit / self.directory


@dataclass(config=ConfigDict(validate_assignment=True))
class PumpProbeParameters(DataClassJsonMixin):
    pump_exp: float
    pump_delay: float
    pump_status: bool = False
    pump_repeat: str = "0"
    prepump_exp: Optional[float] = None

    def __post_init__(self):
        if self.pump_exp and self.pump_exp > 0:
            self.pump_status = True


@dataclass(config=ConfigDict(validate_assignment=True))
class ExtruderParams(DataClassJsonMixin):
    num_imgs: int
    expt_type: str = "extruder"


@dataclass(config=ConfigDict(validate_assignment=True))
class FixedTargetParams(DataClassJsonMixin):
    chip_type: str
    map_type: str
    n_exposures: int
    expt_type: str = "fixed_target"


class ExperimentParameters(BaseModel):
    general: GeneralParameters
    pump_probe: PumpProbeParameters
    expt: ExtruderParams | FixedTargetParams  # type: ignore

    class Config:
        arbitrary_types_allowed = True
        smart_union = True

    @classmethod
    def from_file(cls, filename: str):
        with open(filename) as f:
            raw_params = json.load(f)
        return cls(**raw_params)
