from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Tuple

from dataclasses_json import DataClassJsonMixin

from mx_bluesky.I24.serial.parameters.constants import PARAM_FILE_PATH
from mx_bluesky.I24.serial.setup_beamline import (
    Detector,
    ExperimentType,
    Extruder,
    FixedTarget,
    caget,
)


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
            # If file name ends in a digit this causes processing/pilatus pain.
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


def read_parameters(
    expt: ExperimentType, det_type: Detector
) -> Tuple[Dict[str, Any], Path]:
    # There's probably a better way but it will do for now
    params: Dict[str, Any] = {}
    general = GeneralParameters(
        visit=caget(expt.pv.visit),
        directory=caget(expt.pv.directory),
        filename=caget(expt.pv.filename),
        exp_time=float(caget(expt.pv.exp_time)),
        det_type=det_type.name,
        det_dist=float(caget(expt.pv.det_dist)),
    )
    filepath = general.collection_path
    params.update(**general.to_dict())

    if isinstance(expt, Extruder):
        params["num_imgs"] = float(caget(expt.spec_pv.num_imgs))
        pp = PumpProbeParameters(
            pump_exp=float(caget(expt.pv.pump_exp)),
            pump_delay=float(caget(expt.pv.pump_delay)),
            pump_status=bool(caget(expt.spec_pv.pump_status)),
        )
    elif isinstance(expt, FixedTarget):
        params["chip_type"] = caget(expt.spec_pv.chip_type)
        params["map_type"] = caget(expt.spec_pv.map_type)
        params["n_exposures"] = int(caget(expt.spec_pv.n_exposures))
        pp = PumpProbeParameters(
            pump_exp=float(caget(expt.pv.pump_exp)),
            pump_delay=float(caget(expt.pv.pump_delay)),
            pump_repeat=caget(expt.spec_pv.pump_repeat),
            prepump_exp=float(caget(expt.spec_pv.prepump_exp)),
        )
    params.update(**pp.to_dict())
    return params, filepath


def write_params_to_file(
    params: Dict[str, Any],
    filepath: Path | str = PARAM_FILE_PATH,
    expt_type: str = "FT",
):
    if not isinstance(filepath, Path):
        filepath = Path(filepath)

    with open(filepath / f"{expt_type}_parameters.txt", "w") as fh:
        for k, v in params.items():
            fh.write(f"{k} \t\t{v}\n")
