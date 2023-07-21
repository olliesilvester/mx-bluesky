import logging
import subprocess

from mx_bluesky.I24.serial import log


def setup_logging():
    logger = logging.getLogger("I24ssx")
    log.config("edm_screen.log")
    return logger


def run_extruder():
    logger = setup_logging()
    logger.info("Starting extruder edm screen.")
    subprocess.run(
        [
            "edm",
            "/dls_sw/i24/software/bluesky/mx_bluesky/src/mx_bluesky/I24/serial/extruder/EX-gui-edm/DiamondExtruder-I24-py3v1.edl",
        ]
    )
    logger.info("Edm screen closed.")


def run_fixed_target():
    logger = setup_logging()
    logger.info("Starting extruder edm screen.")
    subprocess.run(
        [
            "edm",
            "/dls_sw/i24/software/bluesky/mx_bluesky/src/mx_bluesky/I24/serial/fixed_target/FT-gui-edm/DiamondChipI24-py3v1.edl",
        ]
    )
    logger.info("Edm screen closed.")
