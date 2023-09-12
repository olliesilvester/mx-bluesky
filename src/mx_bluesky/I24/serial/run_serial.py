import logging
import subprocess
from os import environ
from pathlib import Path

from mx_bluesky.I24.serial import log


def setup_logging():
    logger = logging.getLogger("I24ssx")
    log.config("edm_screen.log")
    return logger


def get_location(default: str = "dev") -> str:
    return environ.get("BEAMLINE") or default


def get_edm_path() -> Path:
    return Path(__file__).parents[4] / "edm_serial"


def run_extruder():
    logger = setup_logging()
    loc = get_location()
    logger.info(f"Running on {loc}.")
    edm_path = get_edm_path()
    logger.info("Starting extruder edm screen...")
    subprocess.run(
        [
            "edm",
            "-x",
            edm_path / "EX-gui/DiamondExtruder-I24-py3v1.edl",
        ]
    )
    logger.info("Edm screen closed.")


def run_fixed_target():
    logger = setup_logging()
    loc = get_location()
    logger.info(f"Running on {loc}.")
    edm_path = get_edm_path()
    logger.info("Starting fixed target edm screen...")
    subprocess.run(
        [
            "edm",
            "-x",
            edm_path / "FT-gui/DiamondChipI24-py3v1.edl",
        ]
    )
    logger.info("Edm screen closed.")
