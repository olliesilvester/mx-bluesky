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
    Pilatus,
)

logger = logging.getLogger("I24ssx.sup_det")


def setup_logging():
    logfile = time.strftime("SSXdetectorOps_%d%B%y.log").lower()
    log.config(logfile)


class UnknownDetectorType(Exception):
    pass


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


def _move_detector_stage(detector_stage: DetectorMotion, target: float):
    logger.info(f"Moving detector stage to target position: {target}.")
    yield from bps.abs_set(
        detector_stage.y,
        target,
        wait=True,
    )


def setup_detector_stage(detector_stage: DetectorMotion, expt_type: str):
    # Grab the correct PV depending on experiment
    # Its value is set with MUX on edm screen
    det_type = pv.me14e_gp101 if expt_type == "fixed-target" else pv.ioc12_gp15
    requested_detector = caget(det_type)
    logger.info(f"Requested detector: {requested_detector}.")
    det_y_target = (
        Eiger.det_y_target if "eiger" in requested_detector else Pilatus.det_y_target
    )
    yield from _move_detector_stage(detector_stage, det_y_target)
    logger.info("Detector setup done.")


if __name__ == "__main__":
    setup_logging()
    RE = RunEngine()
    # Use dodal device for move
    detector_stage = i24.detector_motion()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "expt",
        type=str,
        choices=["extruder", "fixed-target"],
        help="Type of serial experiment being run.",
    )

    args = parser.parse_args()
    RE(setup_detector_stage(detector_stage, args.expt))
