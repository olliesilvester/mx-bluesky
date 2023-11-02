import logging

from mx_bluesky.I24.serial.setup_beamline import pv
from mx_bluesky.I24.serial.setup_beamline.ca import caget  # , caput
from mx_bluesky.I24.serial.setup_beamline.pv_abstract import Detector, Eiger, Pilatus

logger = logging.getLogger("I24ssx.sup_det")


class UnknownDetectorType(Exception):
    pass


def get_detector_type() -> Detector:
    det_y = caget(pv.det_y)
    if float(det_y) < Eiger.det_y_threshold:
        logger.info("Eiger detector in use.")
        return Eiger()
    elif float(det_y) > Pilatus.det_y_threshold:
        logger.info("Pilatus detector in use.")
        return Pilatus()
    else:
        logger.error("Detector not found.")
        raise UnknownDetectorType("Detector not found.")


def move_detector_stage(expt_type: str):
    print(expt_type)
    # detector_pv = pv.me14e_gp101
    pass


if __name__ == "__main__":
    move_detector_stage("fixed_target")
