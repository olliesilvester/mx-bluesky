# write, scrape and whatever all go in here
# Parameters in common: general setup(visit, filename), pp(aside frm pump repeat I
# guess), detector(type, dist)
# Need something for the chip map stuff

# Something to write file (although I'd rather avoid the write-read steps and just set)

# Also needs to write the userlog file at the end with a summary or something
# in visit/processing/directory/filename_params.txt
# (once all the parameters are in order this might be trivial)

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from mx_bluesky.I24.serial.parameters.constants import PARAM_FILE_PATH
from mx_bluesky.I24.serial.setup_beamline import (
    Detector,
    ExperimentType,
    Extruder,
    FixedTarget,
    caget,
)


@dataclass
class GeneralParameters:
    visit: Path | str
    directory: Path | str
    filename: str
    exp_time: float
    det_type: str
    det_dist: float

    def __post_init__(self):
        if not isinstance(self.visit, Path):
            self.visit = Path(self.visit)

    @property
    def collection_path(self):
        return self.visit / self.directory / self.filename


@dataclass
class PumpProbeParameters:
    pump_exp: float
    pump_delay: float
    pump_status: bool = False
    pump_repeat: str = "0"
    prepump_exp: float | None = None


def read_parameters(expt: ExperimentType, det_type: Detector) -> Dict[str, Any]:
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
    params.update(**general.__dict__)

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
    params.update(**pp.__dict__)
    return params


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
