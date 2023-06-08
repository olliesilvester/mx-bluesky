# write, scrape and whatever all go in here
# Parameters in common: general setup(visit, filename), pp(aside frm pump repeat I
# guess), detector(type, dist)
# Need something for the chip map stuff

# Something to write file (although I'd rather avoid the write-read steps and just set)

# Also needs to write the userlog file at the end with a summary or something
# in visit/processing/directory/filename_params.txt
# (once all the parameters are in order this might be trivial)

from __future__ import annotations

from mx_bluesky.I24.serial.setup_beamline import ExperimentType


class ExperimentParameters:
    def __init__(self, expt: ExperimentType):
        self.visit = expt.pv.visit


def set_parameters():
    pass


def write_parameter_file():
    pass


if __name__ == "__main__":
    set_parameters()
