"""
Extruder data collection
This version in python3 new Feb2021 by RLO
    - March 21 added logging and Eiger functionality
"""
from __future__ import annotations

import argparse
import inspect
import logging
import pathlib
import sys
import time
from datetime import datetime
from time import sleep

from mx_bluesky.I24.serial import log
from mx_bluesky.I24.serial.dcid import DCID, SSXType
from mx_bluesky.I24.serial.setup_beamline import caget, caput, pv
from mx_bluesky.I24.serial.setup_beamline import setup_beamline as sup
from mx_bluesky.I24.serial.write_nexus import call_nexgen

logger = logging.getLogger("I24ssx.extruder")


def setup_logging():
    logfile = time.strftime("i24_%d%B%y.log").lower()
    log.config(logfile)


def flush_print(text):
    sys.stdout.write(str(text))
    sys.stdout.flush()


def initialise_extruderi24():
    name = inspect.stack()[0][3]
    print("Initialise Parameters for extruder data collection")
    logger.info("%s I24 extruder initialisation" % name)

    visit = caget(pv.ioc12_gp1)
    logger.info("%s Visit defined %s" % (name, visit))

    # Define detector in use
    det_type = sup.get_detector_type()

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
    print("Done Done Done")
    logger.info("%s Initialsation complete" % name)


def moveto(place):
    name = inspect.stack()[0][3]
    logger.info("%s Move to %s" % (name, place))

    det_type = caget(pv.ioc12_gp15)

    if place == "laseron":
        logger.info("%s laser on%s" % (name, place))
        if det_type == "pilatus":
            caput(pv.zebra1_out1_ttl, 60.0)
            caput(pv.zebra1_soft_in_b0, 1.0)
        elif det_type == "eiger":
            caput(pv.zebra1_out2_ttl, 60.0)
            caput(pv.zebra1_soft_in_b0, 1.0)

    if place == "laseroff":
        logger.info("%s laser off%s" % (name, place))
        if det_type == "pilatus":
            caput(pv.zebra1_soft_in_b0, 0.0)
            caput(pv.zebra1_out1_ttl, 0.0)
        elif det_type == "eiger":
            caput(pv.zebra1_soft_in_b0, 0.0)
            caput(pv.zebra1_out2_ttl, 0.0)

    if place == "enterhutch":
        caput(pv.det_z, 1480)


def write_parameter_file():
    name = inspect.stack()[0][3]

    param_path = "/dls_sw/i24/scripts/extruder/"
    param_fid = "parameters.txt"

    logger.info("%s Writing Parameter File \n%s" % (name, param_path + param_fid))
    print("\nWriting Parameter File   ", param_path + param_fid)

    visit = caget(pv.ioc12_gp1)
    directory = caget(pv.ioc12_gp2)
    filename = caget(pv.ioc12_gp3)
    num_imgs = caget(pv.ioc12_gp4)
    exp_time = caget(pv.ioc12_gp5)
    det_dist = caget(pv.ioc12_gp7)
    det_type = caget(pv.ioc12_gp15)
    if int(caget(pv.ioc12_gp6)) == 1:
        pump_status = "true"
    else:
        pump_status = "false"
    pump_exp = caget(pv.ioc12_gp9)
    pump_delay = caget(pv.ioc12_gp10)

    # If file name ends in a digit this causes processing/pilatus pain.
    # Append an underscore
    numbers = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")
    if det_type == "pilatus":
        if filename.endswith(numbers):
            # Note for future reference. Appending underscore causes more hassle and
            # high probability of users accidentally overwriting data. Use a dash
            filename = filename + "-"
            print("Requested filename ends in a number. Appended dash:", filename)
            logger.info("%s Requested filename ends in a number. Appended dash")

    f = open(param_path + param_fid, "w")
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
    f.close()

    logger.info("%s visit %s" % (name, visit))
    logger.info("%s directory %s" % (name, directory))
    logger.info("%s filename %s" % (name, filename))
    logger.info("%s num_imgs %s" % (name, num_imgs))
    logger.info("%s exp_time %s" % (name, exp_time))
    logger.info("%s det_dist %s" % (name, det_dist))
    logger.info("%s det_type %s" % (name, det_type))
    logger.info("%s pump_probe %s" % (name, pump_status))
    logger.info("%s pump_exp %s" % (name, pump_exp))
    logger.info("%s pump_delay %s" % (name, pump_delay))

    print("\n")
    print("visit:", visit)
    print("directory:", directory)
    print("filename:", filename)
    print("num_imgs:", num_imgs)
    print("exp_time:", exp_time)
    print("det_dist:", det_dist)
    print("det_type:", det_type)
    print("pump_probe:", pump_status)
    print("pump_exp:", pump_exp)
    print("pump_delay:", pump_delay)


def scrape_parameter_file():
    param_path = "/dls_sw/i24/scripts/extruder/"
    with open(param_path + "parameters.txt", "r") as filein:
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


def run_extruderi24():
    print("Starting i24")
    name = inspect.stack()[0][3]
    logger.info("%s" % name)

    start_time = datetime.now()
    print("Start time", start_time.ctime())

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

    logger.info("%s Start Time = % s" % (name, start_time))

    # Setting up the beamline
    caput("BL24I-PS-SHTR-01:CON", "Reset")
    print("Reset hutch shutter sleep for 1sec")
    sleep(1.0)
    caput("BL24I-PS-SHTR-01:CON", "Open")
    print("Open hutch shutter sleep for 2sec")
    sleep(2.0)

    sup.beamline("collect")
    sup.beamline("quickshot", [det_dist])

    # Set the abort PV to zero
    caput(pv.ioc12_gp8, 0)

    # For pixel detector
    filepath = visit + directory
    print("Filepath", filepath)
    print("Filename", filename)
    logger.info("%s Filepath %s" % (name, filepath))
    logger.info("%s Filename %s" % (name, filename))

    # For zebra
    # The below will need to be determined emprically. A value of 0.0 may be ok (????)
    probepumpbuffer = 0.01

    gate_start = 1.0
    # Need to check these for pilatus. Added temprary hack in pilatus pump is false below as gate width wrong
    gate_width = float(pump_exp) + float(pump_delay) + float(exp_time)
    gate_step = float(gate_width) + float(probepumpbuffer)
    print("Calculated gate width", gate_width)
    print("Calculated gate step", gate_step)
    num_gates = num_imgs
    p1_delay = 0
    p1_width = pump_exp
    p2_delay = pump_delay
    p2_width = exp_time

    if det_type == "pilatus":
        print("Using pilatus mini cbf")
        caput(pv.pilat_cbftemplate, 0)
        logger.info("%s Pilatus quickshot setup: filepath %s" % (name, filepath))
        logger.info("%s Pilatus quickshot setup: filepath %s" % (name, filename))
        logger.info(
            "%s Pilatus quickshot setup: number of images %s" % (name, num_imgs)
        )
        logger.info("%s Pilatus quickshot setup: exposure time %s" % (name, exp_time))

        if pump_status == "true":
            print("pump probe experiment")
            logger.info("%s Pump probe extruder data collection" % name)
            logger.info("%s Pump exposure time %s" % (name, pump_exp))
            logger.info("%s Pump delay time %s" % (name, pump_delay))
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
            print("Static experiment: no photoexcitation")
            logger.info("%s Static experiment: no photoexcitation" % name)
            sup.pilatus("quickshot", [filepath, filename, num_imgs, exp_time])
            gate_start = 1.0
            gate_width = (float(exp_time) * float(num_imgs)) + float(0.5)
            sup.zebra1("quickshot", [gate_start, gate_width])

    elif det_type == "eiger":
        # Test moving seqID+1 to here
        caput(pv.eiger_seqID, int(caget(pv.eiger_seqID)) + 1)
        logger.info("%s Eiger quickshot setup: filepath %s" % (name, filepath))
        logger.info("%s Eiger quickshot setup: filepath %s" % (name, filename))
        logger.info("%s Eiger quickshot setup: number of images %s" % (name, num_imgs))
        logger.info("%s Eiger quickshot setup: exposure time %s" % (name, exp_time))

        if pump_status == "true":
            print("pump probe experiment")
            logger.info("%s Pump probe extruder data collection" % name)
            logger.info("%s Pump exposure time %s" % (name, pump_exp))
            logger.info("%s Pump delay time %s" % (name, pump_delay))
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
            print("Static experiment: no photoexcitation")
            logger.info("%s Static experiment: no photoexcitation" % name)
            gate_start = 1.0
            gate_width = (float(exp_time) * float(num_imgs)) + float(0.5)
            sup.eiger("quickshot", [filepath, filename, num_imgs, exp_time])
            sup.zebra1("quickshot", [gate_start, gate_width])
    else:
        logger.warning("%s Unknown Detector Type, det_type = %s" % (name, det_type))
        print("Unknown detector type")

    # Do DCID creation BEFORE arming the detector
    dcid = DCID(
        emit_errors=False,
        ssx_type=SSXType.EXTRUDER,
        visit=pathlib.Path(visit).name,
        image_dir=filepath,
        start_time=start_time,
        num_images=num_imgs,
        exposure_time=exp_time,
    )

    # Collect
    print("\nFast Shutter Opening")
    logger.info("%s Fast shutter opened" % (name))
    caput(pv.zebra1_soft_in_b1, 1)
    if det_type == "pilatus":
        print("pilatus acquire ON")
        caput(pv.pilat_acquire, 1)
    elif det_type == "eiger":
        print("Triggering Eiger NOW")
        caput(pv.eiger_trigger, 1)

    dcid.notify_start()

    param_file_tuple = scrape_parameter_file()
    if det_type == "eiger":
        call_nexgen(None, start_time, param_file_tuple, "extruder")

    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

    aborted = False
    while True:
        # ioc12_gp8 is the ABORT button
        if int(caget(pv.ioc12_gp8)) == 0:
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
                    logger.warning("%s Data Collection Aborted" % (name))
                    print(50 * "ABORTED ")
                    if det_type == "pilatus":
                        caput(pv.pilat_acquire, 0)
                    elif det_type == "eiger":
                        caput(pv.eiger_acquire, 0)
                    sleep(1.0)
                    break
                elif int(caget(pv.zebra1_pc_arm_out)) != 1:
                    print("----> Zebra disarmed  <----")
                    print(20 * "DONE ")
                    break
        else:
            aborted = True
            print("Data Collection ended due to GP 8 not equalling 0")
            logger.warning(
                "%s Data Collection ended due to GP 8 not equalling 0" % (name)
            )
            break
        break
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

    caput(pv.ioc12_gp8, 1)
    print("\nFast Shutter Closing")
    logger.info("%s Fast shutter closed" % (name))
    caput(pv.zebra1_soft_in_b1, 0)
    print("\nZebra DISARMED")
    caput(pv.zebra1_pc_disarm, 1)

    end_time = datetime.now()

    if det_type == "pilatus":
        print("Pilatus Acquire STOP")
        caput(pv.pilat_acquire, 0)
    elif det_type == "eiger":
        print("Eiger Acquire STOP")
        caput(pv.eiger_acquire, 0)
        caput(pv.eiger_ODcapture, "Done")
        print(filename + "_" + caget(pv.eiger_seqID))
        print(type(num_imgs))

    sleep(0.5)

    # Clean Up
    # print 'Setting zebra back to normal'
    sup.zebra1("return-to-normal")
    if det_type == "pilatus":
        sup.pilatus("return-to-normal")
    elif det_type == "eiger":
        sup.eiger("return-to-normal")
        print(filename + "_" + caget(pv.eiger_seqID))
        # Write eiger return to normal next
    print("End of Run ")
    print("Close hutch shutter")
    caput("BL24I-PS-SHTR-01:CON", "Close")

    dcid.collection_complete(end_time, aborted=aborted)
    dcid.notify_end()
    print("Start time", start_time.ctime())
    print("End time", end_time.ctime())
    logger.info("%s End Time = %s" % (name, end_time))
    return 1


usage = "%(prog)s command [options]"
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


def main():
    setup_logging()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
