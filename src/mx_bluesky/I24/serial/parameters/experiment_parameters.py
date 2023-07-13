from __future__ import annotations

import json
import re
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from pydantic import BaseModel
from pydantic.dataclasses import dataclass


@dataclass
class GeneralParameters(DataClassJsonMixin):
    visit: Path | str
    directory: Path | str
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


@dataclass
class PumpProbeParameters(DataClassJsonMixin):
    pump_exp: float
    pump_delay: float
    pump_status: bool = False
    pump_repeat: str = "0"
    prepump_exp: float | None = None

    def __post_init__(self):
        if self.pump_exp and self.pump_exp > 0:
            self.pump_status = True


@dataclass
class ExtruderParams(DataClassJsonMixin):
    num_imgs: int


@dataclass
class FixedTargetParams(DataClassJsonMixin):
    chip_type: str
    map_type: str
    n_exposures: int


class ExperimentParameters(BaseModel):
    general: GeneralParameters
    pump_probe: PumpProbeParameters
    expt: ExtruderParams | FixedTargetParams

    class Config:
        arbitrary_types_allowed = True
        smart_union = True

    @classmethod
    def from_file(cls, filename: str):
        with open(filename) as f:
            raw_params = json.load(f)
        return cls(**raw_params)
