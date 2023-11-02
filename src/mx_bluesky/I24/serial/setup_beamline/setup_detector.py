"""
Utilities for defining the detector in use, and moving the stage.
"""
import argparse
import logging
import time

from mx_bluesky.I24.serial import log
from mx_bluesky.I24.serial.setup_beamline import pv
from mx_bluesky.I24.serial.setup_beamline.ca import caget  # , caput
from mx_bluesky.I24.serial.setup_beamline.pv_abstract import (
    Detector,
    Eiger,
    ExperimentType,
    Extruder,
    FixedTarget,
    Pilatus,
)

logger = logging.getLogger("I24ssx.sup_det")


def setup_logging():
    # Log should now change name daily.
    logfile = time.strftime("SSXdetectorOps_%d%B%y.log").lower()
    log.config(logfile)


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


def move_detector_stage():
    "Plan goes here"
    pass


def setup_detector_stage(expt_type: str):
    expt: ExperimentType
    expt = FixedTarget() if expt_type == "fixed-target" else Extruder()
    print(expt.expt_type)
    current_detector = get_detector_type().name
    logger.info(
        f"Detector type PV for {expt_type} currently set to: {current_detector}."
    )
    requested_detector = caget(expt.pv.det_type)
    logger.info(f"Requested detector: {requested_detector}.")
    if current_detector == requested_detector:
        print("do nothing")
    else:
        print("call plan to move")
    logger.info("Detector setup done.")


if __name__ == "__main__":
    setup_logging()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "expt",
        type=str,
        choices=["extruder", "fixed-target"],
        help="Type of serial experiment being run.",
    )

    args = parser.parse_args()
    setup_detector_stage(args.expt)
