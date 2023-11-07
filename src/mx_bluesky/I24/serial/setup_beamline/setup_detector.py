"""
Utilities for defining the detector in use, and moving the stage.
"""
import argparse
import logging
import time

import bluesky.plan_stubs as bps
from bluesky.run_engine import RunEngine
from dodal.beamlines import i24
from dodal.devices.i24.I24_detector_motion import DetectorMotion

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
    logfile = time.strftime("SSXdetectorOps_%d%B%y.log").lower()
    log.config(logfile)


class UnknownDetectorType(Exception):
    pass


def _read_detector_stage_position(det_stage: DetectorMotion):
    yield from bps.rd(det_stage.y)
    yield from bps.rd(det_stage.z)


def get_detector_type() -> Detector:
    det_y = caget(pv.det_y)
    # Note to self, I should also be able to use detmotion for this too!
    if float(det_y) < Eiger.det_y_threshold:
        logger.info("Eiger detector in use.")
        return Eiger()
    elif float(det_y) > Pilatus.det_y_threshold:
        logger.info("Pilatus detector in use.")
        return Pilatus()
    else:
        logger.error("Detector not found.")
        raise UnknownDetectorType("Detector not found.")


def check_detector_position(det_stage: DetectorMotion, tolerance: int = 10):
    """Check that detector is in the right position (ie if pilatus not in place \
    for eiger) and/or that it's within allowed range (see tolerance)
    """
    det_y = yield from bps.rd(det_stage.y)
    print(det_y)


def move_detector_stage(det_stage: DetectorMotion, target: float):
    yield from bps.abs_set(
        det_stage.y,
        target,
    )
    "Plan goes here"


def setup_detector_stage(expt_type: str):
    expt: ExperimentType
    expt = FixedTarget() if expt_type == "fixed-target" else Extruder()
    detector_stage = i24.detector_motion()
    current_detector = get_detector_type().name
    logger.info(
        f"Detector type PV for {expt_type} currently set to: {current_detector}."
    )
    requested_detector = caget(expt.pv.det_type)  # Set with MUX on edm screen
    logger.info(f"Requested detector: {requested_detector}.")
    RE = RunEngine()
    if current_detector == requested_detector:
        # check that the position is actually correct, if not move
        logger.info("Detector already in place")
    else:
        det_y_target = (
            Eiger.det_y_target
            if "eiger" in requested_detector
            else Pilatus.det_y_target
        )
        RE(move_detector_stage(detector_stage, det_y_target))
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
