"""
Extruder data collection
This version in python3 new Feb2021 by RLO
    - March 21 added logging and Eiger functionality
"""
from __future__ import annotations

import argparse
import logging
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from time import sleep

from mx_bluesky.I24.serial import log
from mx_bluesky.I24.serial.dcid import DCID
from mx_bluesky.I24.serial.parameters import SSXType
from mx_bluesky.I24.serial.parameters.constants import PARAM_FILE_PATH
from mx_bluesky.I24.serial.setup_beamline import caget, caput, pv
from mx_bluesky.I24.serial.setup_beamline import setup_beamline as sup
from mx_bluesky.I24.serial.setup_beamline.setup_detector import get_detector_type
from mx_bluesky.I24.serial.write_nexus import call_nexgen

usage = "%(prog)s command [options]"
logger = logging.getLogger("I24ssx.extruder")


def setup_logging():
    logfile = time.strftime("i24extruder_%d%B%y.log").lower()
    log.config(logfile)


def flush_print(text):
    sys.stdout.write(str(text))
    sys.stdout.flush()


def _coerce_to_path(path: Path | str) -> Path:
    if not isinstance(path, Path):
        return Path(path)
    return path


@log.log_on_entry
def initialise_extruderi24(args=None):
    logger.info("Initialise Parameters for extruder data collection on I24.")

    visit = caget(pv.ioc12_gp1)
    logger.info("Visit defined %s" % visit)

    # Define detector in use
    det_type = get_detector_type()

    caput(pv.ioc12_gp2, "test")
    caput(pv.ioc12_gp3, "testrun")
    caput(pv.ioc12_gp4, "100")
    caput(pv.ioc12_gp5, "0.01")
    caput(pv.ioc12_gp6, 0)
    caput(pv.ioc12_gp8, 0)  # status PV do not reuse gp8 for something else
    caput(pv.ioc12_gp9, 0)
    caput(pv.ioc12_gp10, 0)
    caput(pv.ioc12_gp15, det_type.name)
    caput(pv.pilat_cbftemplate, 0)
    logger.info("Initialisation complete.")


@log.log_on_entry
def moveto(args):
    place = args.place
    logger.info("Move to: %s" % place)

    det_type = get_detector_type()

    if place == "laseron":
        if det_type == "pilatus":
            caput(pv.zebra1_out1_ttl, 60.0)
            caput(pv.zebra1_soft_in_b0, 1.0)
        elif det_type == "eiger":
            caput(pv.zebra1_out2_ttl, 60.0)
            caput(pv.zebra1_soft_in_b0, 1.0)

    if place == "laseroff":
        if det_type == "pilatus":
            caput(pv.zebra1_soft_in_b0, 0.0)
            caput(pv.zebra1_out1_ttl, 0.0)
        elif det_type == "eiger":
            caput(pv.zebra1_soft_in_b0, 0.0)
            caput(pv.zebra1_out2_ttl, 0.0)

    if place == "enterhutch":
        caput(pv.det_z, 1480)


@log.log_on_entry
def write_parameter_file(param_path: Path | str = PARAM_FILE_PATH):
    param_path = _coerce_to_path(param_path)
    param_fid = "parameters.txt"

    logger.info("Writing Parameter File to: %s \n" % (param_path / param_fid))

    visit = caget(pv.ioc12_gp1)
    directory = caget(pv.ioc12_gp2)
    filename = caget(pv.ioc12_gp3)
    num_imgs = caget(pv.ioc12_gp4)
    exp_time = caget(pv.ioc12_gp5)
    det_dist = caget(pv.ioc12_gp7)
    det_type = get_detector_type()
    if int(caget(pv.ioc12_gp6)) == 1:
        pump_status = "true"
    else:
        pump_status = "false"
    pump_exp = caget(pv.ioc12_gp9)
    pump_delay = caget(pv.ioc12_gp10)

    # If file name ends in a digit this causes processing/pilatus pain.
    # Append an underscore
    if det_type == "pilatus":
        m = re.search(r"\d+$", filename)
        if m is not None:
            # Note for future reference. Appending underscore causes more hassle and
            # high probability of users accidentally overwriting data. Use a dash
            filename = filename + "-"
            logger.info(
                "Requested filename ends in a number. Appended dash: %s" % filename
            )

    with open(param_path / param_fid, "w") as f:
        f.write("visit \t\t%s\n" % visit)
        f.write("directory \t%s\n" % directory)
        f.write("filename \t%s\n" % filename)
        f.write("num_imgs \t%s\n" % num_imgs)
        f.write("exp_time \t%s\n" % exp_time)
        f.write("det_dist \t%s\n" % det_dist)
        f.write("det_type \t%s\n" % det_type)
        f.write("pump_probe \t%s\n" % pump_status)
        f.write("pump_exp \t%s\n" % pump_exp)
        f.write("pump_delay \t%s\n" % pump_delay)

    logger.info("Parameters \n")
    logger.info("visit %s" % visit)
    logger.info("directory %s" % directory)
    logger.info("filename %s" % filename)
    logger.info("num_imgs %s" % num_imgs)
    logger.info("exp_time %s" % exp_time)
    logger.info("det_dist %s" % det_dist)
    logger.info("det_type %s" % det_type)
    logger.info("pump_probe %s" % pump_status)
    logger.info("pump_exp %s" % pump_exp)
    logger.info("pump_delay %s" % pump_delay)


def scrape_parameter_file(param_path: Path | str = PARAM_FILE_PATH):
    param_path = _coerce_to_path(param_path)

    with open(param_path / "parameters.txt", "r") as filein:
        f = filein.readlines()
    for line in f:
        entry = line.rstrip().split()
        if line.startswith("visit"):
            visit = entry[1]
        elif line.startswith("directory"):
            directory = entry[1]
        elif line.startswith("filename"):
            filename = entry[1]
        elif "num_imgs" in entry[0].lower():
            num_imgs = entry[1]
        elif "exp_time" in entry[0].lower():
            exp_time = entry[1]
        elif "det_dist" in entry[0].lower():
            det_dist = entry[1]
        elif "det_type" in entry[0].lower():
            det_type = entry[1]
        elif "pump_probe" in entry[0].lower():
            pump_status = entry[1]
        elif "pump_exp" in entry[0].lower():
            pump_exp = entry[1]
        elif "pump_delay" in entry[0].lower():
            pump_delay = entry[1]
    return (
        visit,
        directory,
        filename,
        num_imgs,
        exp_time,
        det_dist,
        det_type,
        pump_status,
        pump_exp,
        pump_delay,
    )


@log.log_on_entry
def run_extruderi24(args=None):
    start_time = datetime.now()
    logger.info("Collection start time: %s" % start_time.ctime())

    write_parameter_file()
    (
        visit,
        directory,
        filename,
        num_imgs,
        exp_time,
        det_dist,
        det_type,
        pump_status,
        pump_exp,
        pump_delay,
    ) = scrape_parameter_file()

    # Setting up the beamline
    caput("BL24I-PS-SHTR-01:CON", "Reset")
    logger.debug("Reset hutch shutter sleep for 1sec")
    sleep(1.0)
    caput("BL24I-PS-SHTR-01:CON", "Open")
    logger.debug("Open hutch shutter sleep for 2sec")
    sleep(2.0)

    sup.beamline("collect")
    sup.beamline("quickshot", [det_dist])

    # Set the abort PV to zero
    caput(pv.ioc12_gp8, 0)

    # For pixel detector
    filepath = visit + directory
    logger.info("Filepath %s" % filepath)
    logger.info("Filename %s" % filename)

    # For zebra
    # The below will need to be determined emprically. A value of 0.0 may be ok (????)
    probepumpbuffer = 0.01

    gate_start = 1.0
    # Need to check these for pilatus.
    # Added temprary hack in pilatus pump is false below as gate width wrong
    gate_width = float(pump_exp) + float(pump_delay) + float(exp_time)
    gate_step = float(gate_width) + float(probepumpbuffer)
    logger.info("Calculated gate width %.4f" % gate_width)
    logger.info("Calculated gate step %.4f" % gate_step)
    num_gates = num_imgs
    p1_delay = 0
    p1_width = pump_exp
    p2_delay = pump_delay
    p2_width = exp_time

    if det_type == "pilatus":
        logger.debug("Using pilatus mini cbf")
        caput(pv.pilat_cbftemplate, 0)
        logger.info("Pilatus quickshot setup: filepath %s" % filepath)
        logger.info("Pilatus quickshot setup: filepath %s" % filename)
        logger.info("Pilatus quickshot setup: number of images %d" % num_imgs)
        logger.info("Pilatus quickshot setup: exposure time %s" % exp_time)

        if pump_status == "true":
            logger.info("Pump probe extruder data collection")
            logger.info("Pump exposure time %s" % pump_exp)
            logger.info("Pump delay time %s" % pump_delay)
            sup.pilatus("fastchip", [filepath, filename, num_imgs, exp_time])
            sup.zebra1(
                "zebratrigger-pilatus",
                [
                    gate_start,
                    gate_width,
                    num_gates,
                    gate_step,
                    p1_delay,
                    p1_width,
                    p2_delay,
                    p2_width,
                ],
            )
        elif pump_status == "false":
            logger.info("Static experiment: no photoexcitation")
            sup.pilatus("quickshot", [filepath, filename, num_imgs, exp_time])
            gate_start = 1.0
            gate_width = (float(exp_time) * float(num_imgs)) + float(0.5)
            sup.zebra1("quickshot", [gate_start, gate_width])

    elif det_type == "eiger":
        logger.info("Using Eiger detector")

        logger.warning(
            """TEMPORARY HACK!
            Running a Single image pilatus data collection to create directory."""
        )  # See https://github.com/DiamondLightSource/mx_bluesky/issues/45
        num_shots = 1
        sup.pilatus("quickshot-internaltrig", [filepath, filename, num_shots, exp_time])
        logger.debug("Sleep 2s waiting for pilatus to arm")
        sleep(2.5)
        caput(pv.pilat_acquire, "0")  # Disarm pilatus
        sleep(0.5)
        caput(pv.pilat_acquire, "1")  # Arm pilatus
        logger.debug("Pilatus data collection DONE")
        sup.pilatus("return to normal")
        logger.info("Pilatus back to normal. Single image pilatus data collection DONE")

        caput(pv.eiger_seqID, int(caget(pv.eiger_seqID)) + 1)
        logger.info("Eiger quickshot setup: filepath %s" % filepath)
        logger.info("Eiger quickshot setup: filepath %s" % filename)
        logger.info("Eiger quickshot setup: number of images %s" % num_imgs)
        logger.info("Eiger quickshot setup: exposure time %s" % exp_time)

        if pump_status == "true":
            logger.info("Pump probe extruder data collection")
            logger.info("Pump exposure time %s" % pump_exp)
            logger.info("Pump delay time %s" % pump_delay)
            sup.eiger("triggered", [filepath, filename, num_imgs, exp_time])
            sup.zebra1(
                "zebratrigger-eiger",
                [
                    gate_start,
                    gate_width,
                    num_gates,
                    gate_step,
                    p1_delay,
                    p1_width,
                    p2_delay,
                    p2_width,
                ],
            )
        elif pump_status == "false":
            logger.info("Static experiment: no photoexcitation")
            gate_start = 1.0
            gate_width = (float(exp_time) * float(num_imgs)) + float(0.5)
            sup.eiger("quickshot", [filepath, filename, num_imgs, exp_time])
            sup.zebra1("quickshot", [gate_start, gate_width])
    else:
        err = "Unknown Detector Type, det_type = %s" % det_type
        logger.error(err)
        raise ValueError(err)

    # Do DCID creation BEFORE arming the detector
    dcid = DCID(
        emit_errors=False,
        ssx_type=SSXType.EXTRUDER,
        visit=Path(visit).name,
        image_dir=filepath,
        start_time=start_time,
        num_images=num_imgs,
        exposure_time=exp_time,
    )

    # Collect
    logger.info("Fast shutter opening")
    caput(pv.zebra1_soft_in_b1, 1)
    if det_type == "pilatus":
        logger.info("Pilatus acquire ON")
        caput(pv.pilat_acquire, 1)
    elif det_type == "eiger":
        logger.info("Triggering Eiger NOW")
        caput(pv.eiger_trigger, 1)

    dcid.notify_start()

    param_file_tuple = scrape_parameter_file()
    if det_type == "eiger":
        logger.info("Call nexgen server for nexus writing.")
        call_nexgen(None, start_time, param_file_tuple, "extruder")

    aborted = False
    timeout_time = time.time() + int(num_imgs) * float(exp_time) + 10

    if int(caget(pv.ioc12_gp8)) == 0:  # ioc12_gp8 is the ABORT button
        caput(pv.zebra1_pc_arm, 1)
        sleep(gate_start)
        i = 0
        text_list = ["|", "/", "-", "\\"]
        while True:
            line_of_text = "\r\t\t\t Waiting   " + 30 * ("%s" % text_list[i % 4])
            flush_print(line_of_text)
            sleep(0.5)
            i += 1
            if int(caget(pv.ioc12_gp8)) != 0:
                aborted = True
                logger.warning("Data Collection Aborted")
                if det_type == "pilatus":
                    caput(pv.pilat_acquire, 0)
                elif det_type == "eiger":
                    caput(pv.eiger_acquire, 0)
                sleep(1.0)
                break
            elif int(caget(pv.zebra1_pc_arm_out)) != 1:
                # As soon as the zebra1_pc_arm_out is not 1 anymore, exit.
                # Epics checks the geobrick and updates this PV once the collection is done.
                logger.info("----> Zebra disarmed  <----")
                break
            elif time.time() >= timeout_time:
                logger.warning(
                    """
                    Something went wrong and data collection timed out. Aborting.
                """
                )
                if det_type == "pilatus":
                    caput(pv.pilat_acquire, 0)
                elif det_type == "eiger":
                    caput(pv.eiger_acquire, 0)
                sleep(1.0)
                break
    else:
        aborted = True
        logger.warning("Data Collection ended due to GP 8 not equalling 0")

    caput(pv.ioc12_gp8, 1)
    logger.info("Fast shutter closing")
    caput(pv.zebra1_soft_in_b1, 0)
    logger.info("\nZebra DISARMED")
    caput(pv.zebra1_pc_disarm, 1)

    end_time = datetime.now()

    if det_type == "pilatus":
        logger.info("Pilatus Acquire STOP")
        caput(pv.pilat_acquire, 0)
    elif det_type == "eiger":
        logger.info("Eiger Acquire STOP")
        caput(pv.eiger_acquire, 0)
        caput(pv.eiger_ODcapture, "Done")

    sleep(0.5)

    # Clean Up
    logger.info("Setting zebra back to normal")
    sup.zebra1("return-to-normal")
    if det_type == "pilatus":
        sup.pilatus("return-to-normal")
    elif det_type == "eiger":
        sup.eiger("return-to-normal")
        print(filename + "_" + caget(pv.eiger_seqID))
    logger.info("End of Run")
    logger.info("Close hutch shutter")
    caput("BL24I-PS-SHTR-01:CON", "Close")

    dcid.collection_complete(end_time, aborted=aborted)
    dcid.notify_end()
    logger.info("End Time = %s" % end_time.ctime())
    return 1


if __name__ == "__main__":
    setup_logging()

    parser = argparse.ArgumentParser(usage=usage, description=__doc__)
    subparsers = parser.add_subparsers(
        help="Choose command.",
        required=True,
        dest="sub-command",
    )

    parser_init = subparsers.add_parser(
        "initialise",
        description="Initialise extruder on beamline I24.",
    )
    parser_init.set_defaults(func=initialise_extruderi24)
    parser_run = subparsers.add_parser(
        "run",
        description="Run extruder on I24.",
    )
    parser_run.set_defaults(func=run_extruderi24)
    parser_mv = subparsers.add_parser(
        "moveto",
        description="Move extruder to requested setting on I24.",
    )
    parser_mv.add_argument(
        "place",
        type=str,
        choices=["laseron", "laseroff", "enterhutch"],
        help="Requested setting.",
    )
    parser_mv.set_defaults(func=moveto)

    args = parser.parse_args()
    args.func(args)
