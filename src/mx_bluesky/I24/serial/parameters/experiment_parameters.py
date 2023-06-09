# write, scrape and whatever all go in here
# Parameters in common: general setup(visit, filename), pp(aside frm pump repeat I
# guess), detector(type, dist)
# Need something for the chip map stuff

# Something to write file (although I'd rather avoid the write-read steps and just set)

# Also needs to write the userlog file at the end with a summary or something
# in visit/processing/directory/filename_params.txt
# (once all the parameters are in order this might be trivial)

from __future__ import annotations

from pathlib import Path

from mx_bluesky.I24.serial.parameters.constants import PARAM_FILE_PATH
from mx_bluesky.I24.serial.setup_beamline import (
    Detector,
    ExperimentType,
    Extruder,
    FixedTarget,
    caget,
)


class ExperimentParameters:
    def __init__(self, expt: ExperimentType, det_type: Detector):
        self.expt = expt
        self.det_type = det_type

    def read_parameters(self):
        # There's definitely a better way but for now this might work
        return {
            "visit": caget(self.expt.pv.visit),
            "directory": caget(self.expt.pv.directory),
            "filename": caget(self.expt.pv.filename),
            "exp_time": float(caget(self.expt.pv.exp_time)),
            "det_type": self.det_type.name,
            "det_dist": float(caget(self.expt.pv.det_dist)),
            "pump_exp": float(caget(self.expt.pv.pump_exp)),
            "pump_delay": float(caget(self.expt.pv.pump_delay)),
        }

    def collection_path(self):
        visit = Path(caget(self.expt.pv.visit))
        directory = Path(caget(self.expt.pv.directory))
        filename = caget(self.expt.pv.filename)
        return visit / directory / filename


class ExtruderParameters(ExperimentParameters):
    PARAM_FILE_NAME = "extruder_parameters.txt"

    def __init__(self, expt: Extruder, det_type: Detector):
        super().__init__(expt, det_type)

    def read_parameters(self):
        params = ExperimentParameters.read_parameters(self)
        params["num_imgs"] = float(caget(self.expt.spec_pv.num_imgs))
        params["pump_status"] = bool(caget(self.expt.spec_pv.pump_status))
        return params

    def get_params(self):
        return tuple(self.read_parameters().values())

    def write_to_file(self, filepath: Path | str = PARAM_FILE_PATH):
        if not isinstance(filepath, Path):
            filepath = Path(filepath)

        params = self.read_parameters()
        with open(filepath / self.PARAM_FILE_NAME, "w") as fh:
            for k, v in params.items():
                fh.write(f"{k} \t\t{v}\n")


class FixedTargetParameters(ExperimentParameters):
    PARAM_FILE_NAME = "fixedtarget_parameters.txt"

    def __init__(self, expt: FixedTarget, det_type: Detector):
        super().__init__(expt, det_type)

    def read_parameters(self):
        params = ExperimentParameters.read_parameters(self)
        params["chip_type"] = caget(self.expt.spec_pv.chip_type)
        params["map_type"] = caget(self.expt.spec_pv.map_type)
        params["n_exposures"] = int(caget(self.expt.spec_pv.n_exposures))
        params["pump_repeat"] = caget(self.expt.spec_pv.pump_repeat)
        params["prepump_exp"] = float(caget(self.expt.spec_pv.prepump_exp))
        return params

    def get_params(self):
        return tuple(self.read_parameters().values())

    def write_to_file(self, filepath: Path | str = PARAM_FILE_PATH):
        if not isinstance(filepath, Path):
            filepath = Path(filepath)

        params = self.read_parameters()
        with open(filepath / self.PARAM_FILE_NAME, "w") as fh:
            for k, v in params.items():
                fh.write(f"{k} \t\t{v}\n")
