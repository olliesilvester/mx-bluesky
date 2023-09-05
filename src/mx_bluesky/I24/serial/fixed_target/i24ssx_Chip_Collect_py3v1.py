"""
Fixed target data collection
"""
from __future__ import annotations

import logging
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
from time import sleep

import numpy as np

from mx_bluesky.I24.serial import log
from mx_bluesky.I24.serial.dcid import DCID, SSXType
from mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_StartUp_py3v1 import (
    get_format,
    scrape_parameter_file,
)
from mx_bluesky.I24.serial.parameters.constants import LITEMAP_PATH, PARAM_FILE_PATH_FT
from mx_bluesky.I24.serial.setup_beamline import caget, cagetstring, caput, pv
from mx_bluesky.I24.serial.setup_beamline import setup_beamline as sup
from mx_bluesky.I24.serial.write_nexus import call_nexgen

logger = logging.getLogger("I24ssx.fixed_target")

usage = "%(prog)s [options]"


def setup_logging():
    # Log should now change name daily.
    logfile = time.strftime("i24fixedtarget_%d%B%y.log").lower()
    log.config(logfile)


def flush_print(text):
    sys.stdout.write(str(text))
    sys.stdout.flush()


def copy_files_to_data_location(
    dest_dir: Path | str,
    param_path: Path = PARAM_FILE_PATH_FT,
    map_file: Path = LITEMAP_PATH,
    map_type: str = "1",
):
    if not isinstance(dest_dir, Path):
        dest_dir = Path(dest_dir)
    shutil.copy2(param_path / "parameters.txt", dest_dir / "parameters.txt")
    if map_type == "1":
        shutil.copy2(map_file / "currentchip.map", dest_dir / "currentchip.map")


@log.log_on_entry
def get_chip_prog_values(
    chip_type,
    pump_repeat,
    pumpexptime,
    pumpdelay,
    prepumpexptime,
    exptime=16,
    n_exposures=1,
):
    if chip_type in ["0", "1", "3"]:
        logger.info("This is an Oxford chip %s" % chip_type)
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
        logger.info("This is a Custom Chip")
        x_num_steps = caget(pv.me14e_gp6)
        y_num_steps = caget(pv.me14e_gp7)
        x_step_size = caget(pv.me14e_gp8)
        y_step_size = caget(pv.me14e_gp99)
        xblocks = 1
        yblocks = 1
        x_block_size = 0  # placeholder
        y_block_size = 0  # placeholder
    else:
        logger.warning("Unknown chip_type, chip_type = %s" % chip_type)

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
        logger.warning("Unknown pump_repeat, pump_repeat = %s" % pump_repeat)

    logger.info("Pump repeat is %s, PVAR set to %s" % (pump_repeat, pump_repeat_pvar))

    if pump_repeat == "2":
        pump_in_probe = 1
    else:
        pump_in_probe = 0

    logger.info("pump_in_probe set to %s" % pump_in_probe)

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


@log.log_on_entry
def load_motion_program_data(motion_program_dict, map_type, pump_repeat):
    logger.info("Loading motion program data for chip.")
    logger.info("Pump_repeat is %s" % pump_repeat)
    if pump_repeat == "0":
        if map_type == "0":
            prefix = 11
            logger.info(
                "Map type is %s, setting program prefix to %s" % (map_type, prefix)
            )
        elif map_type == "1":
            prefix = 12
        elif map_type == "2":
            prefix = 13
        else:
            logger.warning("Unknown Map Type, map_type = %s" % map_type)
            return
    elif pump_repeat in ["1", "2", "3", "4", "5", "6", "7"]:
        prefix = 14
        logger.info("Setting program prefix to %s" % prefix)
    else:
        logger.warning("Unknown Pump repeat, pump_repeat = %s" % pump_repeat)
        return

    logger.info("Set PMAC_STRING pv.")
    for key in sorted(motion_program_dict.keys()):
        v = motion_program_dict[key]
        pvar_base = prefix * 100
        pvar = pvar_base + v[0]
        value = str(v[1])
        s = "P%s=%s" % (str(pvar), str(value))
        logger.info("%s \t %s" % (key, s))
        caput(pv.me14e_pmac_str, s)
        sleep(0.02)
    sleep(0.2)


@log.log_on_entry
def get_prog_num(chip_type, map_type, pump_repeat):
    logger.info("Get Program Number")
    if str(pump_repeat) == "0":
        if chip_type in ["0", "1"]:
            logger.info("Pump_repeat: %s \tOxford Chip: %s" % (pump_repeat, chip_type))
            if map_type == "0":
                logger.info("Map type 0 = None")
                logger.info("Program number: 11")
                return 11
            elif map_type == "1":
                logger.info("Map type 1 = Mapping Lite")
                logger.info("Program number: 12")
                return 12
            elif map_type == "2":
                logger.info("Map type 1 = Full Mapping")
                logger.info("Program number: 13")  # once fixed return 13
                msg = "Mapping Type FULL is broken as of 11.09.17"
                logger.error(msg)
                raise ValueError(msg)
            else:
                logger.debug("Unknown Mapping Type; map_type = %s" % map_type)
                return 0
        elif chip_type == "2":
            logger.info("Pump_repeat: %s \tCustom Chip: %s" % (pump_repeat, chip_type))
            logger.info("Program number: 11")
            return 11
        elif chip_type == "3":
            logger.info(
                "Pump_repeat: %s \tMini Oxford Chip: %s" % (pump_repeat, chip_type)
            )
            logger.info("Program number: 11")
            return 11
        else:
            logger.debug("Unknown chip_type, chip_tpe = = %s" % chip_type)
            return 0
    elif pump_repeat in ["1", "2", "3", "4", "5", "6", "7"]:
        logger.info("Pump_repeat: %s \t Chip Type: %s" % (pump_repeat, chip_type))
        logger.info("Map Type = Mapping Lite with Pump Probe")
        logger.info("Program number: 14")
        return 14
    else:
        logger.warning("Unknown pump_repeat, pump_repeat = = %s" % pump_repeat)
        return 0


@log.log_on_entry
def datasetsizei24():
    # Calculates how many images will be collected based on map type and N repeats
    logger.info("Calculate total number of images expected in data collection.")
    (
        chip_name,
        visit,
        sub_dir,
        n_exposures,
        chip_type,
        map_type,
        pump_repeat,
        pumpexptime,
        pumpdelay,
        exptime,
        dcdetdist,
        prepumpexptime,
        det_type,
    ) = scrape_parameter_file()

    if map_type == "0":
        if chip_type == "2":
            total_numb_imgs = int(int(caget(pv.me14e_gp6)) * int(caget(pv.me14e_gp7)))
            logger.info(
                "Map type: None \tCustom chip \tNumber of images %s" % total_numb_imgs
            )
        else:
            chip_format = get_format(chip_type)[:4]
            total_numb_imgs = np.prod(chip_format)
            logger.info(
                "Map type: None \tOxford chip %s \tNumber of images %s"
                % (chip_type, total_numb_imgs)
            )

    elif map_type == "1":
        logger.info("Using Mapping Lite on chip type %s" % chip_type)
        chip_format = get_format(chip_type)[2:4]
        block_count = 0
        with open(LITEMAP_PATH / "currentchip.map", "r") as f:
            for line in f.readlines():
                entry = line.split()
                if entry[2] == "1":
                    block_count += 1

        logger.info("Block count=%s" % block_count)
        logger.info("Chip format=%s" % chip_format)

        n_exposures = int(caget(pv.me14e_gp3))
        logger.info("Number of exposures=%s" % n_exposures)

        total_numb_imgs = np.prod(chip_format) * block_count * n_exposures
        logger.info("Calculated number of images: %s" % total_numb_imgs)

    elif map_type == "2":
        logger.error("Not Set Up For Full Mapping")
        raise ValueError("The beamline is currently not set for Full Mapping.")

    else:
        logger.warning("Unknown Map Type, map_type = %s" % map_type)
        raise ValueError("Unknown map type")

    logger.info("Set PV to calculated number of images.")
    caput(pv.me14e_gp10, total_numb_imgs)

    return total_numb_imgs


@log.log_on_entry
def start_i24():
    """Returns a tuple of (start_time, dcid)"""
    logger.info("Start I24 data collection.")
    start_time = datetime.now()
    logger.info("Collection start time %s" % start_time.ctime())

    (
        chip_name,
        visit,
        sub_dir,
        n_exposures,
        chip_type,
        map_type,
        pump_repeat,
        pumpexptime,
        pumpdelay,
        exptime,
        dcdetdist,
        prepumpexptime,
        det_type,
    ) = scrape_parameter_file()

    logger.debug("Set up beamline")
    sup.beamline("collect")
    sup.beamline("quickshot", [dcdetdist])
    logger.debug("Set up beamline DONE")

    total_numb_imgs = datasetsizei24()

    filepath = visit + sub_dir
    filename = chip_name

    logger.debug("Acquire Region")

    num_gates = int(total_numb_imgs) / int(n_exposures)

    logger.info("Total number of images: %d" % total_numb_imgs)
    logger.info("Number of exposures: %s" % n_exposures)
    logger.info("Number of gates (=Total images/N exposures): %.4f" % num_gates)

    if det_type == "pilatus":
        logger.info("Using Pilatus detector")
        logger.info("Fastchip Pilatus setup: filepath %s" % filepath)
        logger.info("Fastchip Pilatus setup: filepath %s" % filename)
        logger.info("Fastchip Pilatus setup: number of images %d" % total_numb_imgs)
        logger.info("Fastchip Pilatus setup: exposure time %s" % exptime)

        sup.pilatus("fastchip", [filepath, filename, total_numb_imgs, exptime])

        # DCID process depends on detector PVs being set up already
        logger.debug("Start DCID process")
        dcid = DCID(
            emit_errors=False,
            ssx_type=SSXType.FIXED,
            visit=Path(visit).name,
            image_dir=filepath,
            start_time=start_time,
            num_images=total_numb_imgs,
            exposure_time=exptime,
            detector=det_type,
            shots_per_position=int(n_exposures),
            pump_exposure_time=float(pumpexptime),
            pump_delay=float(pumpdelay),
            pump_status=int(pump_repeat),
        )

        logger.debug("Arm Pilatus. Arm Zebra.")
        sup.zebra1("fastchip-pilatus", [num_gates, n_exposures, exptime])
        caput(pv.pilat_acquire, "1")  # Arm pilatus
        caput(pv.zebra1_pc_arm, "1")  # Arm zebra fastchip-pilatus
        caput(pv.pilat_filename, filename)
        time.sleep(1.5)

    elif det_type == "eiger":
        logger.info("Using Eiger detector")

        logger.warning(
            """TEMPORARY HACK!
            Running a Single image pilatus data collection to create directory."""
        )
        num_imgs = 1
        sup.pilatus("quickshot-internaltrig", [filepath, filename, num_imgs, exptime])
        logger.debug("Sleep 2s waiting for pilatus to arm")
        sleep(2)
        sleep(0.5)
        caput(pv.pilat_acquire, "0")  # Disarm pilatus
        sleep(0.5)
        caput(pv.pilat_acquire, "1")  # Arm pilatus
        logger.debug("Pilatus data collection DONE")
        sup.pilatus("return to normal")
        logger.info("Pilatus back to normal. Single image pilatus data collection DONE")

        logger.info("Triggered Eiger setup: filepath %s" % filepath)
        logger.info("Triggered Eiger setup: filename %s" % filename)
        logger.info("Triggered Eiger setup: number of images %d" % total_numb_imgs)
        logger.info("Triggered Eiger setup: exposure time %s" % exptime)

        sup.eiger("triggered", [filepath, filename, total_numb_imgs, exptime])

        # DCID process depends on detector PVs being set up already
        logger.debug("Start DCID process")
        dcid = DCID(
            emit_errors=False,
            ssx_type=SSXType.FIXED,
            visit=Path(visit).name,
            image_dir=filepath,
            start_time=start_time,
            num_images=total_numb_imgs,
            exposure_time=exptime,
            detector=det_type,
        )

        logger.debug("Arm Zebra.")
        sup.zebra1("fastchip-eiger", [num_gates, n_exposures, exptime])
        caput(pv.zebra1_pc_arm, "1")  # Arm zebra fastchip-eiger

        time.sleep(1.5)

    else:
        msg = "Unknown Detector Type, det_type = %s" % det_type
        logger.error(msg)
        raise ValueError(msg)

    # Open the hutch shutter

    caput("BL24I-PS-SHTR-01:CON", "Reset")
    logger.debug("Reset, then sleep for 1s")
    sleep(1.0)
    caput("BL24I-PS-SHTR-01:CON", "Open")
    logger.debug(" Open, then sleep for 2s")
    sleep(2.0)

    return start_time.ctime(), dcid


@log.log_on_entry
def finish_i24(chip_prog_dict, start_time):
    det_type = str(caget(pv.me14e_gp101))
    logger.info("Finish I24 data collection with %s detector." % det_type)

    (
        chip_name,
        visit,
        sub_dir,
        n_exposures,
        chip_type,
        map_type,
        pump_repeat,
        pumpexptime,
        pumpdelay,
        exptime,
        dcdetdist,
        prepumpexptime,
        det_type,
    ) = scrape_parameter_file()

    total_numb_imgs = datasetsizei24()
    filepath = visit + sub_dir
    filename = chip_name
    transmission = (float(caget(pv.pilat_filtertrasm)),)
    wavelength = float(caget(pv.dcm_lambda))

    if det_type == "pilatus":
        logger.info("Finish I24 Pilatus")
        filename = filename + "_" + caget(pv.pilat_filenum)
        logger.debug("Close the fast shutter.")
        caput(pv.zebra1_soft_in_b1, "No")
        logger.debug("Disarm the zebra.")
        caput(pv.zebra1_pc_arm_out, "0")
        sup.zebra1("return-to-normal")
        sup.pilatus("return-to-normal")
        sleep(0.2)
    elif det_type == "eiger":
        logger.info("Finish I24 Eiger")
        logger.debug("Close the fast shutter.")
        caput(pv.zebra1_soft_in_b1, "No")
        logger.debug("Disarm the zebra.")
        caput(pv.zebra1_pc_arm_out, "0")
        sup.zebra1("return-to-normal")
        sup.eiger("return-to-normal")
        filename = cagetstring(pv.eiger_ODfilenameRBV)

    # Detector independent moves
    logger.info("Move chip back to home position by setting PMAC_STRING pv.")
    caput(pv.me14e_pmac_str, "!x0y0z0")
    logger.debug("Closing shutter")
    caput("BL24I-PS-SHTR-01:CON", "Close")

    end_time = time.ctime()
    logger.info("Collection end time %s" % end_time)

    # Copy parameter file and eventual chip map to collection directory
    copy_files_to_data_location(Path(visit + sub_dir), map_type=map_type)

    # Write a record of what was collected to the processing directory
    userlog_path = visit + "processing/" + sub_dir + "/"
    userlog_fid = filename + "_parameters.txt"
    logger.debug("Write a user log in %s" % userlog_path)

    os.makedirs(userlog_path, exist_ok=True)

    with open(userlog_path + userlog_fid, "w") as f:
        f.write("Fixed Target Data Collection Parameters\n")
        f.write("Data directory \t%s\n" % filepath)
        f.write("Filename \t%s\n" % filename)
        f.write("Shots per pos \t%s\n" % n_exposures)
        f.write("Total N images \t%s\n" % total_numb_imgs)
        f.write("Exposure time \t%s\n" % exptime)
        f.write("Det distance \t%s\n" % dcdetdist)
        f.write("Transmission \t%s\n" % transmission)
        f.write("Wavelength \t%s\n" % wavelength)
        f.write("Detector type \t%s\n" % det_type)
        f.write("Pump status \t%s\n" % pump_repeat)
        f.write("Pump exp time \t%s\n" % pumpexptime)
        f.write("Pump delay \t%s\n" % pumpdelay)

    sleep(0.5)

    return end_time


def main():
    # ABORT BUTTON
    logger.info("Running a chip collection on I24")
    caput(pv.me14e_gp9, 0)

    logger.info("Getting parameters from file.")
    (
        chip_name,
        visit,
        sub_dir,
        n_exposures,
        chip_type,
        map_type,
        pump_repeat,
        pumpexptime,
        pumpdelay,
        exptime,
        dcdetdist,
        prepumpexptime,
        det_type,
    ) = scrape_parameter_file()

    logger.info("Chip name is %s" % chip_name)
    logger.info("visit = %s" % visit)
    logger.info("sub_dir = %s" % sub_dir)
    logger.info("n_exposures = %s" % n_exposures)
    logger.info("chip_type = %s" % chip_type)
    logger.info("map_type = %s" % map_type)
    logger.info("dcdetdist = %s" % dcdetdist)
    logger.info("exptime = %s" % exptime)
    logger.info("pump_repeat = %s" % pump_repeat)
    logger.info("pumpexptime = %s" % pumpexptime)
    logger.info("pumpdelay = %s" % pumpdelay)
    logger.info("prepumpexptime = %s" % prepumpexptime)
    logger.info("Getting Program Dictionary")

    # If alignment type is Oxford inner it is still an Oxford type chip
    if str(chip_type) == "1":
        logger.debug("Change chip type Oxford Inner to Oxford.")
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
    logger.info("Loading Motion Program Data")
    load_motion_program_data(chip_prog_dict, map_type, pump_repeat)

    start_time, dcid = start_i24()

    logger.info("Moving to Start")
    caput(pv.me14e_pmac_str, "!x0y0z0")
    sleep(2.0)

    prog_num = get_prog_num(chip_type, map_type, pump_repeat)

    # Now ready for data collection. Open fast shutter
    logger.debug("Opening fast shutter.")
    caput(pv.zebra1_soft_in_b1, "1")  # Open fast shutter (zebra gate)

    logger.info("Run PMAC with program number %d" % prog_num)
    logger.info("pmac str = &2b%dr" % prog_num)
    caput(pv.me14e_pmac_str, "&2b%dr" % prog_num)
    sleep(1.0)

    # Kick off the StartOfCollect script
    logger.debug("Notify DCID of the start of the collection.")
    dcid.notify_start()

    param_file_tuple = scrape_parameter_file()
    if det_type == "eiger":
        logger.debug("Start nexus writing service.")
        call_nexgen(
            chip_prog_dict,
            start_time,
            param_file_tuple,
            total_numb_imgs=datasetsizei24(),
        )

    logger.info("Data Collection running")

    aborted = False
    timeout = time.time() + datasetsizei24() * float(exptime) + 10
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
                    logger.warning("Data Collection Aborted")
                    caput(pv.me14e_pmac_str, "A")
                    sleep(1.0)
                    caput(pv.me14e_pmac_str, "P2401=0")
                    break
                elif int(caget(pv.me14e_scanstatus)) == 0:
                    print(caget(pv.me14e_scanstatus))
                    logger.warning("Data Collection Finished")
                    break
                elif time.time() >= timeout:
                    aborted = True
                    logger.warning(
                        """
                        Something went wrong and data collection timed out. Aborting.
                        """
                    )
                    caput(pv.me14e_pmac_str, "A")
                    sleep(1.0)
                    caput(pv.me14e_pmac_str, "P2401=0")
                    break
        else:
            aborted = True
            logger.info("Data Collection ended due to GP 9 not equalling 0")
            break
        break

    logger.debug("Closing fast shutter")
    caput(pv.zebra1_soft_in_b1, "No")  # Close the fast shutter
    sleep(2.0)

    if det_type == "pilatus":
        logger.debug("Pilatus Acquire STOP")
        sleep(0.5)
        caput(pv.pilat_acquire, 0)
    elif det_type == "eiger":
        logger.debug("Eiger Acquire STOP")
        sleep(0.5)
        caput(pv.eiger_acquire, 0)
        caput(pv.eiger_ODcapture, "Done")

    end_time = finish_i24(chip_prog_dict, start_time)
    dcid.collection_complete(end_time, aborted=aborted)
    logger.debug("Notify DCID of end of collection.")
    dcid.notify_end()

    logger.info("Quick summary of settings")
    logger.info("Chip name = %s sub_dir = %s" % (chip_name, sub_dir))
    logger.info("Start Time = % s" % start_time)
    logger.info("End Time = %s" % end_time)


if __name__ == "__main__":
    setup_logging()

    main()
