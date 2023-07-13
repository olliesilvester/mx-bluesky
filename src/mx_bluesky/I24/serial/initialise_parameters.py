from __future__ import annotations

import argparse
import json

# import logging as lg
from pathlib import Path
from typing import Dict

from mx_bluesky.I24.serial.fixed_target import i24ssx_Chip_StartUp_py3v1 as startup
from mx_bluesky.I24.serial.parameters.constants import PARAM_FILE_PATH, SSXType
from mx_bluesky.I24.serial.parameters.experiment_parameters import (
    ExperimentParameters,
    ExtruderParams,
    FixedTargetParams,
    GeneralParameters,
    PumpProbeParameters,
)
from mx_bluesky.I24.serial.setup_beamline import (
    ExperimentType,
    Extruder,
    FixedTarget,
    caget,
)
from mx_bluesky.I24.serial.setup_beamline import setup_beamline as sup

# logger = logging.getLogger("I24ssx.setup_parameters")

parser = argparse.ArgumentParser()
parser.add_argument(
    "-e",
    "--expt",
    type=str,
    default="FT",
    choices=["EX", "FT"],
)


def read_parameters(
    filepath: Path | str = PARAM_FILE_PATH, expt_type: SSXType = SSXType.FIXED
) -> ExperimentParameters:
    if not isinstance(filepath, Path):
        filepath = Path(filepath)

    root = "FT" if expt_type == SSXType.FIXED else "EX"  # this is horrible

    # Read file
    with open(filepath / f"{root}_parameters.json", "r") as fh:
        data = json.load(fh)

    # Pass to param model
    params = ExperimentParameters.parse_obj(data)
    return params


def write_params_to_file(
    params: Dict,
    filepath: Path | str = PARAM_FILE_PATH,
    expt_type: SSXType = SSXType.FIXED,
):
    if not isinstance(filepath, Path):
        filepath = Path(filepath)

    root = "FT" if expt_type == SSXType.FIXED else "EX"

    with open(filepath / f"{root}_parameters.json", "w") as fh:
        json.dump(params, fh, indent=2)

    # with open(filepath / f"{root}_parameters.txt", "w") as fh:
    #    for k, v in params.items():
    #        fh.write(f"{k} \t\t{v}\n")


def get_params_dict(expt: ExperimentType, det_type: str):
    # params: Dict[str, Any] = {}
    expt_params: FixedTargetParams | ExtruderParams

    # Run caget
    general = GeneralParameters(
        visit=caget(expt.pv.visit),
        directory=caget(expt.pv.directory),
        filename=caget(expt.pv.filename),
        exp_time=float(caget(expt.pv.exp_time)),
        det_type=det_type,
        det_dist=float(caget(expt.pv.det_dist)),
    )
    # params.update(**general.to_dict())
    if isinstance(expt, FixedTarget):
        expt_params = FixedTargetParams(
            chip_type=caget(expt.spec_pv.chip_type),
            map_type=caget(expt.spec_pv.map_type),
            n_exposures=int(caget(expt.spec_pv.n_exposures)),
        )
        # params.update(**expt_params.to_dict())
        pp = PumpProbeParameters(
            pump_exp=float(caget(expt.pv.pump_exp)),
            pump_delay=float(caget(expt.pv.pump_delay)),
            pump_repeat=caget(expt.spec_pv.pump_repeat),
            prepump_exp=float(caget(expt.spec_pv.prepump_exp)),
        )
        # params.update(**pp.to_dict())
    else:
        expt_params = ExtruderParams(num_imgs=int(caget(expt.spec_pv.num_imgs)))
        # params.update(**expt_params.to_dict())
        pp = PumpProbeParameters(
            pump_exp=float(caget(expt.pv.pump_exp)),
            pump_delay=float(caget(expt.pv.pump_delay)),
            pump_status=bool(caget(expt.spec_pv.pump_status)),
        )
        # params.update(**pp.to_dict())

        params = ExperimentParameters(
            general=general,
            pump_probe=pp,
            expt=expt_params,
        )
    return eval(params.json())


def save_parameters(expt_type: SSXType = SSXType.FIXED):
    expt: ExperimentType

    if expt_type == SSXType.FIXED:
        expt = FixedTarget()
    else:
        expt = Extruder()

    # Define detector in use
    det_type = sup.get_detector_type()
    params = get_params_dict(expt, det_type.name)

    # write
    write_params_to_file(params, expt_type=expt_type)

    # For fixed target also call startup.run
    if expt_type == SSXType.FIXED:
        # TODO clean up check_files and write_headers
        startup.run()


def main():
    # setup logging
    args = parser.parse_args()
    expt_type = SSXType.FIXED if args.expt == "FT" else SSXType.EXTRUDER
    save_parameters(expt_type)


if __name__ == "__main__":
    main()
