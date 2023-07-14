"""
Fixed target data collection
"""
from __future__ import annotations

import inspect
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from time import sleep

import numpy as np

from mx_bluesky.I24.serial import log
from mx_bluesky.I24.serial.dcid import DCID

# from mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_Manager_py3v1 import moveto
from mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_StartUp_py3v1 import (  # scrape_parameter_file,
    get_format,
)
from mx_bluesky.I24.serial.initialise_parameters import read_parameters
from mx_bluesky.I24.serial.parameters import ExperimentParameters, SSXType
from mx_bluesky.I24.serial.parameters.constants import LITEMAP_PATH, PARAM_FILE_PATH_FT
from mx_bluesky.I24.serial.setup_beamline import (
    FixedTarget,
    caget,
    cagetstring,
    caput,
    pv,
)
from mx_bluesky.I24.serial.setup_beamline import setup_beamline as sup
from mx_bluesky.I24.serial.write_nexus import call_nexgen

logger = logging.getLogger("I24ssx.fixed_target")

usage = "%(prog)s [options]"


def setup_logging():
    # Log should now change name daily.
    logfile = time.strftime("i24_%Y_%m_%d.log").lower()
    log.config(logfile)


def flush_print(text):
    sys.stdout.write(str(text))
    sys.stdout.flush()


def get_chip_prog_values(
    chip_type,
    pump_repeat,
    pumpexptime,
    pumpdelay,
    prepumpexptime,
    exptime=16,
    n_exposures=1,
):
    name = inspect.stack()[0][3]
    logger.info("%s" % name)
    if chip_type in ["0", "1", "3"]:
        # '1' = 'Oxford ' = [8, 8, 20, 20, 0.125, 3.175, 3.175]
        (
            xblocks,
            yblocks,
            x_num_steps,
            y_num_steps,
            w2w,
            b2b_horz,
            b2b_vert,
        ) = get_format(chip_type)
        x_step_size = w2w
        y_step_size = w2w
        x_block_size = ((x_num_steps - 1) * w2w) + b2b_horz
        y_block_size = ((y_num_steps - 1) * w2w) + b2b_vert

    elif chip_type == "2":
        # This is set by the user in the edm screen
        # The chip format might change every time and is read from PVs.
        print("This is a Custom Chip")
        logger.info("%s This is a Custom Chip" % name)
        x_num_steps = caget(pv.me14e_gp6)
        y_num_steps = caget(pv.me14e_gp7)
        x_step_size = caget(pv.me14e_gp8)
        y_step_size = caget(pv.me14e_gp99)
        xblocks = 1
        yblocks = 1
        x_block_size = 0  # placeholder
        y_block_size = 0  # placeholder
    else:
        print("Unknown chip_type.  oh no")
        logger.warning("%s Unknown chip_type, chip_type = %s" % (name, chip_type))

    # this is where p variables for fast laser expts will be set
    if pump_repeat in ["0", "1", "2"]:
        pump_repeat_pvar = 0
    elif pump_repeat == "3":
        pump_repeat_pvar = 1
    elif pump_repeat == "4":
        pump_repeat_pvar = 2
    elif pump_repeat == "5":
        pump_repeat_pvar = 3
    elif pump_repeat == "6":
        pump_repeat_pvar = 5
    elif pump_repeat == "7":
        pump_repeat_pvar = 10
    else:
        print("Unknown pump_repeat")
        logger.warning("%s Unknown pump_repeat, pump_repeat = %s" % (name, pump_repeat))

    if pump_repeat == "2":
        pump_in_probe = 1
    else:
        pump_in_probe = 0

    chip_dict = {
        "X_NUM_STEPS": [11, x_num_steps],
        "Y_NUM_STEPS": [12, y_num_steps],
        "X_STEP_SIZE": [13, x_step_size],
        "Y_STEP_SIZE": [14, y_step_size],
        "DWELL_TIME": [15, exptime],
        "X_START": [16, 0],
        "Y_START": [17, 0],
        "Z_START": [18, 0],
        "X_NUM_BLOCKS": [20, xblocks],
        "Y_NUM_BLOCKS": [21, yblocks],
        "X_BLOCK_SIZE": [24, x_block_size],
        "Y_BLOCK_SIZE": [25, y_block_size],
        "COLTYPE": [26, 41],
        "N_EXPOSURES": [30, n_exposures],
        "PUMP_REPEAT": [32, pump_repeat_pvar],
        "LASER_DWELL": [34, pumpexptime],
        "LASERTWO_DWELL": [35, prepumpexptime],
        "LASER_DELAY": [37, pumpdelay],
        "PUMP_IN_PROBE": [38, pump_in_probe],
    }

    chip_dict["DWELL_TIME"][1] = 1000 * float(exptime)
    chip_dict["LASER_DWELL"][1] = 1000 * float(pumpexptime)
    chip_dict["LASERTWO_DWELL"][1] = 1000 * float(prepumpexptime)
    chip_dict["LASER_DELAY"][1] = 1000 * float(pumpdelay)

    return chip_dict


def load_motion_program_data(motion_program_dict, map_type, pump_repeat):
    print("Loading prog vars for chip")
    print("pump_repeat", pump_repeat)
    name = inspect.stack()[0][3]
    logger.info("%s loading program variables for chip" % name)
    if pump_repeat == "0":
        print("pump delay is 0")
        if map_type == "0":
            prefix = 11
        elif map_type == "1":
            prefix = 12
        elif map_type == "2":
            prefix = 13
        else:
            logger.warning("%s Unknown Map Type, map_type = %s" % (name, map_type))
            print("Unknown map_type")
    elif pump_repeat in ["1", "2", "3", "4", "5", "6", "7"]:
        print("pump repeat is", pump_repeat)
        prefix = 14
        print("prefix is", prefix)
        # if pump_repeat == '3':
        #    P1432 = 1
        # Need to set the correct P variable here
        #    caput(pv.me14e_pmac_str, 'P1432=1')
        # elif pump_repeat == '4':
        #    P1432 = 2
        #    caput(pv.me14e_pmac_str, 'P1432=2')
        # elif pump_repeat == '5':
        #    P1432 = 3
        #    caput(pv.me14e_pmac_str, 'P1432=3')
        # elif pump_repeat == '6':
        #    P1432 = 5
        #    caput(pv.me14e_pmac_str, 'P1432=5')
        # elif pump_repeat == '3':
        #    P1432 = 10
        #    caput(pv.me14e_pmac_str, 'P1432=10')

    else:
        logger.warning("%s Unknown Pump repeat, pump_repeat = %s" % (name, pump_repeat))
        print("Unknown pump_repeat")

    for key in sorted(motion_program_dict.keys()):
        v = motion_program_dict[key]
        pvar_base = prefix * 100
        pvar = pvar_base + v[0]
        value = str(v[1])
        s = "P" + str(pvar) + "=" + str(value)
        print(key, "\t", s)
        logger.info("%s %s \t %s" % (name, key, s))
        caput(pv.me14e_pmac_str, s)
        sleep(0.02)
    sleep(0.2)
    print("done")
    logger.info("%s done" % name)


def get_prog_num(chip_type, map_type, pump_repeat):
    name = inspect.stack()[0][3]
    logger.info("%s Get Program Number" % name)
    if str(pump_repeat) == "0":
        if chip_type in ["0", "1"]:
            if map_type == "0":
                logger.info("%s\t:Map Type = None" % name)
                print("Map Type is None")
                return 11
            elif map_type == "1":
                logger.info("%s\t:Map Type = Mapping Lite" % name)
                print("Map Type is Mapping Lite")
                return 12
            elif map_type == "2":
                logger.info("%s\t:Map Type = FULL" % name)
                logger.debug("%s\t:Mapping Type FULL is broken as of 11.09.17" % name)
                print("Map Type is FULL")
                return 13
            else:
                logger.debug(
                    "%s\t:Unknown Mapping Type; map_type = %s" % (name, map_type)
                )
                print("Unknown map_type")
                print(map_type)
                return 0
        elif chip_type == "2":
            logger.info("%s\t:Custom Chip" % name)
            print("Custom Chip Type")
            return 11
        elif chip_type == "3":
            logger.info("%s\t:Mini Oxford Chip" % name)
            return 11
        else:
            logger.debug("%s\t:Unknown chip_type, chip_tpe = = %s" % (name, chip_type))
            print("Unknown Chip Type")
            return 0
    elif pump_repeat in ["1", "2", "3", "4", "5", "6", "7"]:
        logger.info("%s\t:Map Type = Mapping Lite with Pump probe" % name)
        print("Map Type is Mapping Lite with Pump Probe")
        return 14
    else:
        logger.debug(
            "%s\t:Unknown pump_repeat, pump_repeat = = %s" % (name, pump_repeat)
        )
        print("Unknown Pump Delay")


def datasetsizei24(params):
    # Calculates how many images will be collected based on map type and N repeats
    name = inspect.stack()[0][3]
    n_exposures = params.expt.n_exposures
    chip_type = params.expt.chip_type
    map_type = params.expt.map_type

    if map_type == "0":
        if chip_type == "2":
            print("Calculating total number of images for custom chip")
            total_numb_imgs = int(int(caget(pv.me14e_gp6)) * int(caget(pv.me14e_gp7)))
            logger.info(
                "%s !!!!!! Calculating total number of images for custom chip %s"
                % (name, total_numb_imgs)
            )
            print(total_numb_imgs)
        else:
            chip_format = get_format(chip_type)[:4]
            total_numb_imgs = np.prod(chip_format)

    elif map_type == "1":
        chip_format = get_format(chip_type)[2:4]
        block_count = 0
        with open(LITEMAP_PATH / "currentchip.map", "r") as f:
            for line in f.readlines():
                entry = line.split()
                if entry[2] == "1":
                    block_count += 1

        print("block_count", block_count)
        print(chip_format)
        logger.info("%s\t:block_count=%s" % (name, block_count))
        logger.info("%s\t:chip_format=%s" % (name, chip_format))

        n_exposures = int(caget(pv.me14e_gp3))
        print(n_exposures)
        logger.info("%s\t:n_exposures=%s" % (name, n_exposures))

        total_numb_imgs = np.prod(chip_format) * block_count * n_exposures

    elif map_type == "2":
        logger.warning("%s\t:Not Set Up For Full Mapping=%s" % (name))
        raise ValueError("The beamline is currently not set for Full Mapping.")

    else:
        logger.warning("%s Unknown Map Type, map_type = %s" % (name, map_type))
        raise ValueError("Unknown map type")

    print("Total number of images", total_numb_imgs, "\n\n\n")
    caput(pv.me14e_gp10, total_numb_imgs)
    logger.info("%s\t:----->Total number of images = %s" % (name, total_numb_imgs))

    return total_numb_imgs


def start_i24(params, filepath):
    """Returns a tuple of (start_time, dcid)"""
    print("Starting i24")
    name = inspect.stack()[0][3]
    logger.info("%s Starting i24" % name)
    start_time = datetime.now()
    # run_num = caget(pv.pilat_filenumber)
    # print(80*'-', run_num)
    # lg.info('%s run_num = %s'%(name,run_num))

    logger.info("%s Set up beamline" % (name))
    sup.beamline("collect")
    sup.beamline("quickshot", [params.general.det_dist])
    logger.info("%s Set up beamline DONE" % (name))

    total_numb_imgs = datasetsizei24(params)

    filename = params.general.filename

    logger.info("%s Filepath %s" % (name, filepath))
    logger.info("%s Filename %s" % (name, filename))
    logger.info("%s Total number images %s" % (name, total_numb_imgs))
    logger.info("%s Exposure time %s" % (name, params.general.exp_time))

    print("Acquire Region")
    logger.info("%s\t:Acquire Region" % (name))

    # Testing for new zebra triggering
    print("ZEBRA TEST ZEBRA TEST ZEBRA TEST ZEBRA TEST")

    num_gates = int(total_numb_imgs) / params.expt.n_exposures

    print("Total number of images:", total_numb_imgs)
    print("Number of exposures:", params.expt.n_exposures)
    print("num gates is Total images/N exposures:", num_gates)

    if params.general.det_type == "pilatus":
        print("Detector type is Pilatus")
        logger.info("%s Fastchip Pilatus setup: filepath %s" % (name, filepath))
        logger.info("%s Fastchip Pilatus setup: filepath %s" % (name, filename))
        logger.info(
            "%s Fastchip Pilatus setup: number of images %s" % (name, total_numb_imgs)
        )
        logger.info(
            "%s Fastchip Pilatus setup: exposure time %s"
            % (name, params.general.exp_time)
        )

        sup.pilatus(
            "fastchip", [filepath, filename, total_numb_imgs, params.general.exp_time]
        )
        # sup.pilatus('fastchip-hatrx', [filepath, filename, total_numb_imgs, exptime])

        # DCID process depends on detector PVs being set up already
        dcid = DCID(
            emit_errors=False,
            ssx_type=SSXType.FIXED,
            visit=params.general.visit.name,
            image_dir=filepath,
            start_time=start_time,
            num_images=total_numb_imgs,
            exposure_time=params.general.exp_time,
            detector=params.general.det_type,
            shots_per_position=params.expt.n_exposures,
            pump_exposure_time=params.pump_probe.pump_exp,
            pump_delay=params.pump_probe.pump_delay,
            pump_status=int(params.pump_probe.pump_repeat),
        )

        print("Arm Pilatus. Arm Zebra.")
        # ZEBRA TEST. Swap the below two lines in/out. Must also swap pc_arm line also.
        # sup.zebra1('fastchip')
        sup.zebra1(
            "fastchip-zebratrigger-pilatus",
            [num_gates, params.expt.n_exposures, params.general.exp_time],
        )
        caput(pv.pilat_acquire, "1")  # Arm pilatus
        caput(pv.zebra1_pc_arm, "1")  # Arm zebra fastchip-pilatus
        caput(pv.pilat_filename, filename)
        time.sleep(1.5)

    elif params.general.det_type == "eiger":
        print("Detector type is Eiger")

        # FIXME TEMPORARY HACK TO DO SINGLE IMAGE PILATUS DATA COLL TO MKDIR #

        print("Single image pilatus data collection to create directory")
        logger.info("%s single image pilatus data collection" % name)
        num_imgs = 1
        sup.pilatus(
            "quickshot-internaltrig",
            [filepath, filename, num_imgs, params.general.exp_time],
        )
        print("Sleep 2s for pilatus to arm")
        sleep(2)
        print("Done. Collecting")
        # caput(pv.pilat_acquire, '1')        # Arm pilatus
        print("Can sometimes fail to arm")
        sleep(0.5)
        caput(pv.pilat_acquire, "0")  # Disarm pilatus
        sleep(0.5)
        caput(pv.pilat_acquire, "1")  # Arm pilatus
        print("Pilatus data collection DONE DONE DONE")
        sup.pilatus("return to normal")
        print("Single image pilatus data collection DONE")

        print("Eiger filepath", filepath)
        print("Eiger filename", filename)
        print("Eiger total number of images", total_numb_imgs)
        logger.info("%s Triggered Eiger setup: filepath %s" % (name, filepath))
        logger.info("%s Triggered Eiger setup: filename %s" % (name, filename))
        logger.info(
            "%s Triggered Eiger setup: number of images %s" % (name, total_numb_imgs)
        )
        logger.info(
            "%s Triggered Eiger setup: exposure time %s"
            % (name, params.general.exp_time)
        )

        sup.eiger(
            "triggered", [filepath, filename, total_numb_imgs, params.general.exp_time]
        )

        # DCID process depends on detector PVs being set up already
        dcid = DCID(
            emit_errors=False,
            ssx_type=SSXType.FIXED,
            visit=params.general.visit.name,
            image_dir=filepath,
            start_time=start_time,
            num_images=total_numb_imgs,
            exposure_time=params.general.exp_time,
            detector=params.general.det_type,
            shots_per_position=params.expt.n_exposures,
        )

        print("Arm Zebra.")
        sup.zebra1(
            "fastchip-eiger",
            [num_gates, params.expt.n_exposures, params.general.exp_time],
        )
        caput(pv.zebra1_pc_arm, "1")  # Arm zebra fastchip-eiger

        time.sleep(1.5)

    else:
        logger.warning(
            "%s Unknown Detector Type, det_type = %s" % (name, params.general.det_type)
        )
        print("Unknown detector type")

    # Open the hutch shutter

    caput("BL24I-PS-SHTR-01:CON", "Reset")
    print("Reset sleep for 1sec")
    sleep(1.0)
    caput("BL24I-PS-SHTR-01:CON", "Open")
    print(" Open sleep for 2sec")
    sleep(2.0)

    return start_time.ctime(), dcid


def finish_i24(params, filepath, chip_prog_dict, start_time):
    name = inspect.stack()[0][3]
    det_type = str(caget(pv.me14e_gp101))

    print("Finishing I24")
    logger.info("%s Finishing I24, Detector Type %s" % (name, det_type))

    total_numb_imgs = datasetsizei24(params)
    filename = params.general.filename

    transmission = (float(caget(pv.pilat_filtertrasm)),)
    wavelength = float(caget(pv.dcm_lambda))

    print(filename)
    print(caget(pv.eiger_seqID))

    if det_type == "pilatus":
        print("Finish I24 Pilatus")
        filename = filename + "_" + caget(pv.pilat_filenum)  # FIXME somewhere in params
        caput(pv.zebra1_soft_in_b1, "No")  # Close the fast shutter
        caput(pv.zebra1_pc_arm_out, "0")  # Disarm the zebra
        sup.zebra1("return-to-normal")
        sup.pilatus("return-to-normal")
        sleep(0.2)
    elif det_type == "eiger":
        # THIS SECTION NEEDS TO BE CHECKED CAREFULLY
        print("Finish I24 Eiger")
        caput(pv.zebra1_soft_in_b1, "No")  # Close the fast shutter
        caput(pv.zebra1_pc_arm_out, "0")  # Disarm the zebra
        sup.zebra1("return-to-normal")
        sup.eiger("return-to-normal")
        # print("NEEDS TESTING NEEDS TESTING NEEDS TESTING")
        filename = cagetstring(pv.eiger_ODfilenameRBV)
        # caput(pv.eiger_acquire, 0)
        # caput(pv.eiger_ODcapture, "Done")
        # print(cagetstring(pv.eiger_ODfilenameRBV))
        # print(filename + "_" + caget(pv.eiger_seqID))

    # Detector independent moves
    # Move chip back to home position and close shutter
    print("Closing shutter")
    caput(pv.me14e_pmac_str, "!x0y0z0")
    caput("BL24I-PS-SHTR-01:CON", "Close")

    end_time = time.ctime()

    # Write a record of what was collected to the processing directory
    print("Writing user log")
    userlog_path = params.general.visit / Path("processing") / params.general.directory
    userlog_fid = filename + "_parameters.txt"

    os.makedirs(userlog_path, exist_ok=True)

    with open(userlog_path + userlog_fid, "w") as f:
        f.write("Fixed Target Data Collection Parameters\n")
        f.write("Data directory \t%s\n" % filepath)
        f.write("Filename \t%s\n" % filename)
        f.write("Shots per pos \t%s\n" % params["n_exposures"])
        f.write("Total N images \t%s\n" % total_numb_imgs)
        f.write("Exposure time \t%s\n" % params["exp_time"])
        f.write("Det distance \t%s\n" % params["det_dist"])
        f.write("Transmission \t%s\n" % transmission)
        f.write("Wavelength \t%s\n" % wavelength)
        f.write("Detector type \t%s\n" % det_type)
        f.write("Pump status \t%s\n" % params["pump_repeat"])
        f.write("Pump exp time \t%s\n" % params["pump_exp"])
        f.write("Pump delay \t%s\n" % params["pump_delay"])

    sleep(0.5)

    return end_time


def main():
    # ABORT BUTTON
    name = inspect.stack()[0][3]
    logger.info("%s" % name)
    logger.info("%s Location is I24 \n Starting" % name)
    caput(pv.me14e_gp9, 0)

    params: ExperimentParameters = read_parameters(
        filepath=PARAM_FILE_PATH_FT,
        expt_type=SSXType.FIXED,
    )
    filepath = params.general.collection_path
    params, filepath = read_parameters(FixedTarget, sup.get_detector_type())

    # FIXME horrible temporary thing
    visit = params.general.visit
    sub_dir = params.general.directory
    chip_name = params.general.filename
    exptime = params.general.exp_time
    det_type = params.general.det_type
    dcdetdist = params.general.det_dist
    chip_type = params.expt.chip_type
    map_type = params.expt.map_type
    n_exposures = params.expt.n_exposures
    pumpexptime = params.pump_probe.pump_exp
    pumpdelay = params.pump_probe.pump_delay
    pump_status = params.pump_probe.pump_status  # noqa: F841
    pump_repeat = params.pump_probe.pump_repeat
    prepumpexptime = params.pump_probe.prepump_exp

    print("exptime", exptime)
    print("pump_repeat", pump_repeat)
    print("pumpexptime", pumpexptime)
    print("pumpdelay", pumpdelay)
    print("visit", visit)
    print("dcdetdist", dcdetdist)
    print("n_exposures", n_exposures)
    print("det_type", det_type)
    logger.info("%s exptime = %s" % (name, exptime))
    logger.info("%s visit = %s" % (name, visit))
    logger.info("%s dcdetdist = %s" % (name, dcdetdist))

    print("\n\nChip name is", chip_name)
    print("sub_dir", sub_dir)
    print("n_exposures", n_exposures)
    print("chip_type", chip_type)
    print("map type", map_type)
    print("pump_repeat", pump_repeat)
    print("pumpexptime", pumpexptime)
    print("pumpdelay", pumpdelay)
    print("prepumpexptime", prepumpexptime)
    print("Getting Prog Dictionary")

    logger.info("%s Chip name is %s" % (name, chip_name))
    logger.info("%s sub_dir = %s" % (name, sub_dir))
    logger.info("%s n_exposures = %s" % (name, n_exposures))
    logger.info("%s chip_type = %s" % (name, chip_type))
    logger.info("%s map_type = %s" % (name, map_type))
    logger.info("%s pump_repeat = %s" % (name, pump_repeat))
    logger.info("%s pumpexptime = %s" % (name, pumpexptime))
    logger.info("%s pumpdelay = %s" % (name, pumpdelay))
    logger.info("%s prepumpexptime = %s" % (name, prepumpexptime))
    logger.info("%s Getting Program Dictionary" % (name))

    # If alignment type is Oxford inner it is still an Oxford type chip
    if str(chip_type) == "1":
        logger.debug("%s\tMain: Change chip type Oxford Inner to Oxford." % name)
        chip_type = "0"

    chip_prog_dict = get_chip_prog_values(
        chip_type,
        pump_repeat,
        pumpexptime,
        pumpdelay,
        prepumpexptime,
        exptime=exptime,
        n_exposures=n_exposures,
    )
    print("Loading Motion Program Data")
    logger.info("%s Loading Motion Program Data" % (name))
    load_motion_program_data(chip_prog_dict, map_type, pump_repeat)

    start_time, dcid = start_i24(params, filepath)

    print("Moving to Start")
    logger.info("%s Moving to start" % (name))
    caput(pv.me14e_pmac_str, "!x0y0z0")
    sleep(2.0)

    prog_num = get_prog_num(chip_type, map_type, pump_repeat)
    logger.info("%s prog_num = %s" % (name, prog_num))
    logger.info("%s Resting" % (name))

    # Now ready for data collection. Open fast shutter
    caput(pv.zebra1_soft_in_b1, "1")  # Open fast shutter (zebra gate)

    print("Running pmac program number", prog_num)

    print("pmacing")
    logger.info("%s pmacing" % (name))
    logger.info("%s pmac str = &2b%sr" % (name, prog_num))
    caput(pv.me14e_pmac_str, "&2b%sr" % prog_num)
    sleep(1.0)

    # Kick off the StartOfCollect script
    dcid.notify_start()

    if det_type == "eiger":
        call_nexgen(
            chip_prog_dict,
            start_time,
            params,
            total_numb_imgs=datasetsizei24(),
        )

    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    logger.info("%s Data Collection running" % (name))

    aborted = False
    while True:
        # me14e_gp9 is the ABORT button
        if int(caget(pv.me14e_gp9)) == 0:
            i = 0
            text_list = ["|", "/", "-", "\\"]
            while True:
                line_of_text = "\r\t\t\t Waiting   " + 30 * ("%s" % text_list[i % 4])
                flush_print(line_of_text)
                sleep(0.5)
                i += 1
                if int(caget(pv.me14e_gp9)) != 0:
                    aborted = True
                    logger.warning("%s Data Collection Aborted" % (name))
                    print(50 * "ABORTED ")
                    caput(pv.me14e_pmac_str, "A")
                    sleep(1.0)
                    caput(pv.me14e_pmac_str, "P2401=0")
                    break
                elif int(caget(pv.me14e_scanstatus)) == 0:
                    print(caget(pv.me14e_scanstatus))
                    logger.warning("%s Data Collection Finished" % (name))
                    print("\n", 20 * "DONE ")
                    break
        else:
            aborted = True
            logger.info("%s Data Collection ended due to GP 9 not equalling 0" % (name))
            break
        break
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    print("Closing fast shutter")
    caput(pv.zebra1_soft_in_b1, "No")  # Close the fast shutter
    sleep(2.0)

    if det_type == "pilatus":
        print("Pilatus Acquire STOP")
        sleep(0.5)
        caput(pv.pilat_acquire, 0)
    elif det_type == "eiger":
        print("Eiger Acquire STOP")
        sleep(0.5)
        caput(pv.eiger_acquire, 0)
        caput(pv.eiger_ODcapture, "Done")

    end_time = finish_i24(params, filepath, chip_prog_dict, start_time)
    dcid.collection_complete(end_time, aborted=aborted)
    dcid.notify_end()

    logger.info("%s Chip name = %s sub_dir = %s" % (name, chip_name, sub_dir))
    print("Start time:", start_time)
    logger.info("%s Start Time = % s" % (name, start_time))
    print("End time:  ", end_time)
    logger.info("%s End Time = %s" % (name, end_time))


if __name__ == "__main__":
    setup_logging()

    main()
