import inspect
import logging as lg
import math
import os
import pathlib
import pprint
import re
import string
import subprocess
import sys
import time
import traceback
from datetime import datetime
from time import sleep
from typing import Optional

import numpy as np
import pv_py3 as pv
import requests
import setup_beamline_py3 as sup
from ca_py3 import caget, cagetstring, caput
from i24ssx.dcid import DCID, SSXType
from i24ssx_Chip_Manager_py3v1 import moveto
from i24ssx_Chip_StartUp_py3v1 import get_format, read_parameters, scrape_parameter_file

sys.path.append("/dls_sw/apps/gw56/ssx-tools/src")

# Log should now change name daily.
fh = lg.FileHandler(filename=time.strftime("logs/i24_%Y_%m_%d.log"))
fh.setFormatter(lg.Formatter("%(asctime)s %(levelname)s:   \t%(message)s"))
fh.setLevel(lg.DEBUG)
console = lg.StreamHandler(sys.stdout)
console.setFormatter(lg.Formatter("%(message)s"))
lg.basicConfig(handlers=[fh, console])
#### Old logging
# lg.basicConfig(format='%(asctime)s %(levelname)s:   \t%(message)s',level=lg.DEBUG, filename='i24_march21.log')

######################################################
# COLLECT  COLLECT  COLLECT  COLLECT COLLECT COLLECT #
# This version changed to python3 March2020 by RLO   #
#                                                    #
######################################################


def flush_print(text):
    sys.stdout.write(str(text))
    sys.stdout.flush()


def get_chip_prog_values(
    chip_type,
    location,
    pump_repeat,
    pumpexptime,
    pumpdelay,
    prepumpexptime,
    exptime=16,
    n_exposures=1,
):
    name = inspect.stack()[0][3]
    lg.info("%s" % name)
    #### Hack for sacla3 to bismuth chip type for oxford inner
    if chip_type in ["0", "1", "5", "7", "8", "10"]:
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

        """
        print 'rrrrrrrrrrrrrrrrrrrrrrrrrrrrr'
        print x_num_steps
        print y_num_steps
        print xblocks
        print yblocks
        print w2w
        print b2b_horz
        print b2b_vert
        print x_block_size
        print y_block_size
        print 'rrrrrrrrrrrrrrrrrrrrrrrrrrrrr'
        '0' = 'Toronto' = [9, 9, 12, 12, 0.125, 2.2  , 2.5  ]
        '1' = 'Oxford ' = [8, 8, 20, 20, 0.125, 3.175, 3.175]
        '2' = 'Hamburg' = [3, 3, 53, 53, 0.150, 8.58 , 8.58 ]
        '5' = 'Regina ' = [7, 7, 20, 20, 0.125, 3.7  , 3.7  ]
        """

    elif chip_type == "2":
        if caget(pv.me14e_gp2) == 2:
            print("Full Mapping on Hamburg -> xblocks = 6")
            lg.info("%s Full Mapping on Hamburg -> xblocks = 6" % name)
            xblocks = 6
        else:
            xblocks = 3

    elif chip_type == "3":
        lg.debug("%s\t:Hack for SACLA3 bismuth for oxford inner" % name)
        chip_type = "1"

    elif chip_type == "4":
        print("This is a Bismuth Chip")
        lg.info("%s This is a Bismuth Chip" % name)
        x_num_steps = caget(pv.me14e_gp6)
        y_num_steps = caget(pv.me14e_gp7)
        x_step_size = caget(pv.me14e_gp8)
        y_step_size = x_step_size
        xblocks = 7
        yblocks = 7
        x_block_size = 15  # placeholder
        y_block_size = 15  # placeholder

    elif chip_type == "6":
        print("This is a Custom Chip")
        lg.info("%s This is a Custom Chip" % name)
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
        lg.warning("%s Unknown chip_type, chip_type = %s" % (name, chip_type))

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
        lg.warning("%s Unknown pump_repeat, pump_repeat = %s" % (name, pump_repeat))

    if pump_repeat == "2":
        pump_in_probe = 1
    else:
        pump_in_probe = 0

    chip_dict = {
        "X_NUM_STEPS": [11, x_num_steps],
        "Y_NUM_STEPS": [12, y_num_steps],
        "X_STEP_SIZE": [13, x_step_size],
        "Y_STEP_SIZE": [14, y_step_size],
        "DWELL_TIME": [15, exptime],  # SACLA 15ms + 1ms
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

    if location == "i24":
        chip_dict["DWELL_TIME"][1] = 1000 * float(exptime)
        chip_dict["LASER_DWELL"][1] = 1000 * float(pumpexptime)
        chip_dict["LASERTWO_DWELL"][1] = 1000 * float(prepumpexptime)
        chip_dict["LASER_DELAY"][1] = 1000 * float(pumpdelay)

    return chip_dict


def load_motion_program_data(motion_program_dict, map_type, pump_repeat):
    print("Loading prog vars for chip")
    print("pump_repeat", pump_repeat)
    name = inspect.stack()[0][3]
    lg.info("%s loading program variables for chip" % name)
    if pump_repeat == "0":
        print("pump delay is 0")
        if map_type == "0":
            prefix = 11
        elif map_type == "1":
            prefix = 12
        elif map_type == "2":
            prefix = 13
        else:
            lg.warning("%s Unknown Map Type, map_type = %s" % (name, map_type))
            print("Unknown map_type")
    elif pump_repeat in ["1", "2", "3", "4", "5", "6", "7"]:
        print("pump repeat is", pump_repeat)
        prefix = 14
        print("prefix is", prefix)
        # if pump_repeat == '3':
        #    P1432 = 1
        ############# Need to set the correct P variable here
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
        lg.warning("%s Unknown Pump repeat, pump_repeat = %s" % (name, pump_repeat))
        print("Unknown pump_repeat")

    for key in sorted(motion_program_dict.keys()):
        v = motion_program_dict[key]
        pvar_base = prefix * 100
        pvar = pvar_base + v[0]
        value = str(v[1])
        s = "P" + str(pvar) + "=" + str(value)
        print(key, "\t", s)
        lg.info("%s %s \t %s" % (name, key, s))
        caput(pv.me14e_pmac_str, s)
        sleep(0.02)
    sleep(0.2)
    print("done")
    lg.info("%s done" % name)


def get_prog_num(chip_type, map_type, pump_repeat):
    name = inspect.stack()[0][3]
    lg.info("%s Get Program Number" % name)
    #### Hack for sacla3 to bismuth chip type for oxford inner
    if str(pump_repeat) == "0":
        if str(chip_type) == "3":
            lg.debug("%s\t:Hack for SACLA3 bismuth for oxford inner" % name)
            chip_type = "1"
        if chip_type in ["0", "1", "2", "5", "10"]:
            if map_type == "0":
                lg.info("%s\t:Map Type = None" % name)
                print("Map Type is None")
                return 11
            elif map_type == "1":
                lg.info("%s\t:Map Type = Mapping Lite" % name)
                print("Map Type is Mapping Lite")
                return 12
            elif map_type == "2":
                lg.info("%s\t:Map Type = FULL" % name)
                lg.debug("%s\t:Mapping Type FULL is broken as of 11.09.17" % name)
                print("Map Type is FULL")
                return 13
            else:
                lg.debug("%s\t:Unknown Mapping Type; map_type = %s" % (name, map_type))
                print("Unknown map_type")
                print(map_type)
                return 0
        elif chip_type == "4":
            lg.info("%s\t:Bismuth Chip Type 2" % name)
            print("Bismuth Chip Type 2")
            return 12
        elif chip_type == "6":
            lg.info("%s\t:Custom Chip" % name)
            print("Custom Chip Type")
            return 11
        elif chip_type in ["7", "8"]:
            lg.info("%s\t:Heidelberg Chip" % name)
            print("Heidelberg Chip Type")
            return 11
        else:
            lg.debug("%s\t:Unknown chip_type, chip_tpe = = %s" % (name, chip_type))
            print("Unknown Chip Type")
    elif pump_repeat in ["1", "2", "3", "4", "5", "6", "7"]:
        lg.info("%s\t:Map Type = Mapping Lite with Pump probe" % name)
        print("Map Type is Mapping Lite with Pump Probe")
        return 14
    else:
        lg.debug("%s\t:Unknown pump_repeat, pump_repeat = = %s" % (name, pump_repeat))
        print("Unknown Pump Delay")


def datasetsizei24():
    # Calculates how many images will be collected based on map type and N repeats
    name = inspect.stack()[0][3]
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
    ) = scrape_parameter_file(location="i24")

    if map_type == "0":
        chip_format = get_format(chip_type)[:4]
        if chip_type == "6":
            # Chip Type 6 is Custom
            print("Calculating total number of images")
            total_numb_imgs = int(int(caget(pv.me14e_gp6)) * int(caget(pv.me14e_gp7)))
            lg.info(
                "%s !!!!!! Calculating total number of images %s"
                % (name, total_numb_imgs)
            )
            print(total_numb_imgs)
        else:
            total_numb_imgs = np.prod(chip_format)

    elif map_type == "1":
        chip_format = get_format(chip_type)[2:4]
        block_count = 0
        f = open("/dls_sw/i24/scripts/fastchips/litemaps/currentchip.map", "r")
        for line in f.readlines():
            entry = line.split()
            if entry[2] == "1":
                block_count += 1
        f.close()
        print("block_count", block_count)
        print(chip_format)
        lg.info("%s\t:block_count=%s" % (name, block_count))
        lg.info("%s\t:chip_format=%s" % (name, chip_format))
        ####################
        n_exposures = int(caget(pv.me14e_gp3))
        print(n_exposures)
        lg.info("%s\t:n_exposures=%s" % (name, n_exposures))
        ############################################
        total_numb_imgs = np.prod(chip_format) * block_count * n_exposures
        ############################################
        ############################################
        # For X-ray pump X-ray probe XPXP comment out total_numb_imgs = line above and uncomment below until double line of #####
        # print('X-ray Pump Probe. XPXP. X-ray Pump Probe. XPXP.')
        # if pump_repeat == '0':
        #    total_numb_imgs = np.prod(chip_format) * block_count * n_exposures
        # elif pump_repeat in ['1','3', '4', '5', '6', '7']:
        #    total_numb_imgs = np.prod(chip_format) * block_count * n_exposures * 2
        # else:
        #    print('Unknown pump_repeat')
        ##########################################
        ###########################################

    elif map_type == "2":
        lg.warning("%s\t:Not Set Up For Full Mapping=%s" % (name))
        print("FIX ME, Im not set up for full mapping ")

    else:
        lg.warning("%s Unknown Map Type, map_type = %s" % (name, map_type))
        print("Unknown map type")

    print("Total number of images", total_numb_imgs, "\n\n\n")
    caput(pv.me14e_gp10, total_numb_imgs)
    lg.info("%s\t:----->Total number of images = %s" % (name, total_numb_imgs))

    return total_numb_imgs


def datasetsizesacla():
    chip_name, sub_dir, n_exposures, chip_type, map_type = scrape_parameter_file(
        location="SACLA"
    )
    #### Hack for sacla3 to bismuth chip type for oxford inner

    if str(chip_type) == "3":
        lg.debug("%s\t:Hack for SACLA3 bismuth for oxford inner" % name)
        chip_type = "1"
    if map_type == "0":
        chip_format = get_format(chip_type)[:4]
        total_numb_imgs = np.prod(chip_format)
        if str(chip_type) == "6":
            xs = int(caget(pv.me14e_gp6))
            ys = int(caget(pv.me14e_gp7))
            print(xs, ys, type(xs), type(ys))
            total_numb_imgs = xs * ys
        caput(pv.me14e_gp10, total_numb_imgs)
        caput(pv.me14e_pmac_str, "P2402=0")
        print("Total number of images", total_numb_imgs)

    elif map_type == "1" or map_type == "3":
        chip_format = get_format(chip_type)[2:4]
        block_count = 0
        # f = open('/localhome/local/Documents/sacla/parameter_files/currentchip.map', 'r')
        f = open("/dls_sw/i24/scripts/fastchips/parameter_files/currentchip.map", "r")
        for line in f.readlines():
            entry = line.split()
            if entry[2] == "1":
                block_count += 1
        f.close()
        print("block_count", block_count)
        lg.info("%s\t:block_count=%s" % (name, block_count))
        print(chip_format)
        lg.info("%s\t:chip_format=%s" % (name, chip_format))
        ####################
        n_exposures = caget(pv.me14e_gp3)
        print(n_exposures)
        lg.info("%s\t:n_exposures=%s" % (name, n_exposures))
        ####################
        total_numb_imgs = np.prod(chip_format) * block_count  # * n_exposures
        caput(pv.me14e_gp10, total_numb_imgs)
        caput(pv.me14e_pmac_str, "P2402=0")
        print("Total number of images", total_numb_imgs)

    elif map_type == "2":
        lg.warning("%s Not Set Up For Full Mapping" % name)
        print("FIX ME, Im not set up for full mapping ")
    else:
        lg.warning("%s Unknown Map Type, map_type = %s" % (name, map_type))
        print("Unknown map type")

    return total_numb_imgs


def start_i24():
    """Returns a tuple of (start_time, dcid)"""
    print("Starting i24")
    name = inspect.stack()[0][3]
    lg.info("%s Starting i24" % name)
    start_time = datetime.now()
    # run_num = caget(pv.pilat_filenumber)
    # print(80*'-', run_num)
    # lg.info('%s run_num = %s'%(name,run_num))
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
    ) = scrape_parameter_file(location="i24")

    lg.info("%s Set up beamline" % (name))
    sup.beamline("collect")
    sup.beamline("quickshot", [dcdetdist])
    lg.info("%s Set up beamline DONE" % (name))

    total_numb_imgs = datasetsizei24()

    filepath = visit + sub_dir
    filename = chip_name

    lg.info("%s Filepath %s" % (name, filepath))
    lg.info("%s Filename %s" % (name, filename))
    lg.info("%s Total number images %s" % (name, total_numb_imgs))
    lg.info("%s Exposure time %s" % (name, exptime))

    print("Acquire Region")
    lg.info("%s\t:Acquire Region" % (name))

    #########################################
    # Testing for new zebra triggering
    print("ZEBRA TEST ZEBRA TEST ZEBRA TEST ZEBRA TEST")

    num_gates = int(total_numb_imgs) / int(n_exposures)

    print("Total number of images:", total_numb_imgs)
    print("Number of exposures:", n_exposures)
    print("num gates is Total images/N exposures:", num_gates)

    #########################################

    if det_type == "pilatus":
        print("Detector type is Pilatus")
        lg.info("%s Fastchip Pilatus setup: filepath %s" % (name, filepath))
        lg.info("%s Fastchip Pilatus setup: filepath %s" % (name, filename))
        lg.info(
            "%s Fastchip Pilatus setup: number of images %s" % (name, total_numb_imgs)
        )
        lg.info("%s Fastchip Pilatus setup: exposure time %s" % (name, exptime))

        sup.pilatus("fastchip", [filepath, filename, total_numb_imgs, exptime])
        # sup.pilatus('fastchip-hatrx', [filepath, filename, total_numb_imgs, exptime])

        # DCID process depends on detector PVs being set up already
        dcid = DCID(
            emit_errors=False,
            ssx_type=SSXType.FIXED,
            visit=pathlib.Path(visit).name,
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

        print("Arm Pilatus. Arm Zebra.")
        ###ZEBRA TEST. Swap the below two lines in/out. Must also swap pc_arm line also.
        ###sup.zebra1('fastchip')
        sup.zebra1("fastchip-zebratrigger-pilatus", [num_gates, n_exposures, exptime])
        caput(pv.pilat_acquire, "1")  # Arm pilatus
        caput(pv.zebra1_pc_arm, "1")  # Arm zebra fastchip-zebratrigger
        ###caput(pv.zebra1_pc_arm_out, '1')    # Arm zebra fastchip
        caput(pv.pilat_filename, filename)
        time.sleep(1.5)

    elif det_type == "eiger":
        print("Detector type is Eiger")

        #####################################################################
        ### TEMPORARY HACK TO DO SINGLE IMAGE PILATUS DATA COLL TO MKDIR ####
        #####################################################################
        print("Single image pilatus data collection to create directory")
        lg.info("%s single image pilatus data collection" % name)
        num_imgs = 1
        sup.pilatus("quickshot-internaltrig", [filepath, filename, num_imgs, exptime])
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

        #####################################################################
        #####################################################################

        print("Eiger filepath", filepath)
        print("Eiger filename", filename)
        print("Eiger total number of images", total_numb_imgs)
        lg.info("%s Triggered Eiger setup: filepath %s" % (name, filepath))
        lg.info("%s Triggered Eiger setup: filename %s" % (name, filename))
        lg.info(
            "%s Triggered Eiger setup: number of images %s" % (name, total_numb_imgs)
        )
        lg.info("%s Triggered Eiger setup: exposure time %s" % (name, exptime))

        sup.eiger("triggered", [filepath, filename, total_numb_imgs, exptime])

        # DCID process depends on detector PVs being set up already
        dcid = DCID(
            emit_errors=False,
            ssx_type=SSXType.FIXED,
            visit=pathlib.Path(visit).name,
            image_dir=filepath,
            start_time=start_time,
            num_images=total_numb_imgs,
            exposure_time=exptime,
            detector=det_type,
        )

        print("Arm Zebra.")
        # TO GET DOSE SERIES TO WORK
        # Choose the correct pair of lines
        # sup.zebra1("fastchip-eiger")
        # caput(pv.zebra1_pc_arm_out, '1')    # Arm zebra

        sup.zebra1("fastchip-zebratrigger-eiger", [num_gates, n_exposures, exptime])
        caput(pv.zebra1_pc_arm, "1")  # Arm zebra fastchip-zebratrigger

        time.sleep(1.5)

    else:
        lg.warning("%s Unknown Detector Type, det_type = %s" % (name, det_type))
        print("Unknown detector type")

    ######################################
    # Open the hutch shutter

    caput("BL24I-PS-SHTR-01:CON", "Reset")
    print("Reset sleep for 1sec")
    sleep(1.0)
    caput("BL24I-PS-SHTR-01:CON", "Open")
    print(" Open sleep for 2sec")
    sleep(2.0)

    return start_time.ctime(), dcid


def start_sacla():
    print("Starting SACLA")
    name = inspect.stack()[0][3]
    lg.info("%s Starting SACLA" % name)
    start_time = time.ctime()

    total_numb_imgs = datasetsizesacla()

    ###make sure flipper is out
    moveto("flipperout")
    sleep(1)
    moveto("lightout")
    sleep(3)
    return start_time


def finish_i24(chip_prog_dict, start_time):
    name = inspect.stack()[0][3]
    det_type = str(caget(pv.me14e_gp101))

    print("Finishing I24")
    lg.info("%s Finishing I24, Detector Type %s" % (name, det_type))

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
    ) = scrape_parameter_file(location="i24")

    total_numb_imgs = datasetsizei24()
    filepath = visit + sub_dir
    filename = chip_name
    transmission = (float(caget(pv.pilat_filtertrasm)),)
    wavelength = float(caget(pv.dcm_lambda))

    print(filename)
    print(caget(pv.eiger_seqID))

    if det_type == "pilatus":
        print("Finish I24 Pilatus")
        filename = filename + "_" + caget(pv.pilat_filenum)
        caput(pv.zebra1_soft_in_b1, "No")  # Close the fast shutter
        caput(pv.zebra1_pc_arm_out, "0")  # Disarm the zebra
        sup.zebra1("return-to-normal")
        sup.pilatus("return-to-normal")
        sleep(0.2)
    elif det_type == "eiger":
        ######### THIS SECTION NEEDS TO BE CHECKED CAREFULLY
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
    userlog_path = visit + "processing/" + sub_dir + "/"
    userlog_fid = filename + "_parameters.txt"

    os.makedirs(userlog_path, exist_ok=True)

    f = open(userlog_path + userlog_fid, "w")
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
    f.close()

    # if det_type == 'eiger':
    #    success = call_nexgen(chip_prog_dict, start_time)

    sleep(0.5)

    return end_time


def finish_sacla():
    print("Finishing SACLA")
    name = inspect.stack()[0][3]
    lg.info("%s Finishing SACLA" % name)
    caput(pv.me14e_pmac_str, "!x0y0z0")
    lg.info("%s pmac_str=!x0y0z0" % name)
    end_time = time.ctime()
    return end_time


def call_nexgen(chip_prog_dict, start_time):
    det_type = str(caget(pv.me14e_gp101))
    print(f"det_type: {det_type}")

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
    ) = scrape_parameter_file(location="i24")

    filename_prefix = cagetstring(pv.eiger_ODfilenameRBV)
    meta_h5 = pathlib.Path(visit) / sub_dir / f"{filename_prefix}_meta.h5"
    t0 = time.time()
    max_wait = 60  # seconds
    print(f"Watching for {meta_h5}")
    while time.time() - t0 < max_wait:
        if meta_h5.exists():
            print(f"Found {meta_h5} after {time.time() - t0:.1f} seconds")
            time.sleep(5)
            break
        print(f"Waiting for {meta_h5}")
        time.sleep(1)
    if not meta_h5.exists():
        print(f"Giving up waiting for {meta_h5} after {max_wait} seconds")
        return False

    total_numb_imgs = datasetsizei24()
    # filepath = visit + sub_dir
    # filename = chip_name
    transmission = (float(caget(pv.pilat_filtertrasm)),)
    wavelength = float(caget(pv.dcm_lambda))

    if det_type == "eiger":
        print("nex gen here")
        currentchipmap = (
            "/dls_sw/i24/scripts/fastchips/litemaps/currentchip.map"
            if map_type != 0
            else "fullchip"
        )
        print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        print(chip_prog_dict)

        access_token = pathlib.Path("/scratch/ssx_nexgen.key").read_text().strip()
        url = "https://ssx-nexgen.diamond.ac.uk/ssx_eiger/write"
        headers = {"Authorization": f"Bearer {access_token}"}
        payload = {
            "beamline": "i24",
            "beam_center": [caget(pv.eiger_beamx), caget(pv.eiger_beamy)],
            "chipmap": currentchipmap,
            "chip_info": chip_prog_dict,
            "det_dist": dcdetdist,
            "exp_time": exptime,
            "exp_type": "fixed_target",
            "filename": filename_prefix,
            "num_imgs": int(total_numb_imgs),
            "pump_status": bool(float(pump_repeat)),
            "pump_exp": pumpexptime,
            "pump_delay": pumpdelay,
            "transmission": transmission[0],
            "visitpath": os.fspath(meta_h5.parent),
            "wavelength": wavelength,
        }
        print(f"Sending POST request to {url} with payload:")
        pprint.pprint(payload)
        response = requests.post(url, headers=headers, json=payload)
        print(f"Response: {response.text} (status code: {response.status_code})")
        # the following will raise an error if the request was unsuccessful
        return response.status_code == requests.codes.ok
    return False


def main(location="i24"):
    print("Location is", location, "Starting")
    # ABORT BUTTON
    name = inspect.stack()[0][3]
    lg.info("%s" % name)
    lg.info("%s Location is %s \n Starting" % (name, location))
    caput(pv.me14e_gp9, 0)

    if location == "i24":
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
        ) = scrape_parameter_file(location="i24")
        print("exptime", exptime)
        print("pump_repeat", pump_repeat)
        print("pumpexptime", pumpexptime)
        print("pumpdelay", pumpdelay)
        print("visit", visit)
        print("dcdetdist", dcdetdist)
        print("n_exposures", n_exposures)
        print("det_type", det_type)
        lg.info("%s exptime = %s" % (name, exptime))
        lg.info("%s visit = %s" % (name, visit))
        lg.info("%s dcdetdist = %s" % (name, dcdetdist))
    else:
        (
            chip_name,
            sub_dir,
            n_exposures,
            chip_type,
            map_type,
            prepumpexptime,
        ) = scrape_parameter_file(location="SACLA")

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

    lg.info("%s Chip name is %s" % (name, chip_name))
    lg.info("%s sub_dir = %s" % (name, sub_dir))
    lg.info("%s n_exposures = %s" % (name, n_exposures))
    lg.info("%s chip_type = %s" % (name, chip_type))
    lg.info("%s map_type = %s" % (name, map_type))
    lg.info("%s pump_repeat = %s" % (name, pump_repeat))
    lg.info("%s pumpexptime = %s" % (name, pumpexptime))
    lg.info("%s pumpdelay = %s" % (name, pumpdelay))
    lg.info("%s prepumpexptime = %s" % (name, prepumpexptime))
    lg.info("%s Getting Program Dictionary" % (name))

    ### If alignment type is Oxford inner it is still an Oxford type chip
    if str(chip_type) == "3":
        lg.debug("%s\tMain: Change chip type Oxford Inner to Oxford" % name)
        chip_type = "1"

    if location == "i24":
        chip_prog_dict = get_chip_prog_values(
            chip_type,
            location,
            pump_repeat,
            pumpexptime,
            pumpdelay,
            prepumpexptime,
            exptime=exptime,
            n_exposures=n_exposures,
        )
    else:
        chip_prog_dict = get_chip_prog_values(
            chip_type, location, n_exposures=n_exposures
        )
    print("Loading Motion Program Data")
    lg.info("%s Loading Motion Program Data" % (name))
    load_motion_program_data(chip_prog_dict, map_type, pump_repeat)

    if location == "i24":
        start_time, dcid = start_i24()
    elif location == "SACLA":
        start_time = start_sacla()
    else:
        lg.warning(
            "%s This does nothing location not I24 or SACLA \n location = %s"
            % (name, location)
        )
        lg.debug("%s Put something here... start_time = start_sacla()" % (name))
        print("Something went wrong. Location not specified")

    print("Moving to Start")
    lg.info("%s Moving to start" % (name))
    caput(pv.me14e_pmac_str, "!x0y0z0")
    sleep(2.0)

    prog_num = get_prog_num(chip_type, map_type, pump_repeat)
    lg.info("%s prog_num = %s" % (name, prog_num))
    lg.info("%s Resting" % (name))

    # Now ready for data collection. Open fast shutter
    caput(pv.zebra1_soft_in_b1, "1")  # Open fast shutter (zebra gate)

    print("Running pmac program number", prog_num)

    print("pmacing")
    lg.info("%s pmacing" % (name))
    lg.info("%s pmac str = &2b%sr" % (name, prog_num))
    caput(pv.me14e_pmac_str, "&2b%sr" % prog_num)
    sleep(1.0)

    # Kick off the StartOfCollect script
    dcid.notify_start()

    if location == "i24" and det_type == "eiger":
        success = call_nexgen(chip_prog_dict, start_time)

    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    lg.info("%s Data Collection running" % (name))

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
                    lg.warning("%s Data Collection Aborted" % (name))
                    print(50 * "ABORTED ")
                    caput(pv.me14e_pmac_str, "A")
                    sleep(1.0)
                    caput(pv.me14e_pmac_str, "P2401=0")
                    break
                elif int(caget(pv.me14e_scanstatus)) == 0:
                    print(caget(pv.me14e_scanstatus))
                    lg.warning("%s Data Collection Finished" % (name))
                    print("\n", 20 * "DONE ")
                    break
                # if int(caget(pv.pilat_acquire)) == 'Done':
                #    print '\n', 20*'DONE '
                #    break
        else:
            aborted = True
            lg.info("%s Data Collection ended due to GP 9 not equalling 0" % (name))
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

    if location == "i24":
        end_time = finish_i24(chip_prog_dict, start_time)
        dcid.collection_complete(end_time, aborted=aborted)
        dcid.notify_end()

    if location == "SACLA":
        end_time = finish_sacla()

    lg.info("%s Chip name = %s sub_dir = %s" % (name, chip_name, sub_dir))
    print("Start time:", start_time)
    lg.info("%s Start Time = % s" % (name, start_time))
    print("End time:  ", end_time)
    lg.info("%s End Time = %s" % (name, end_time))


if __name__ == "__main__":
    # main(location='SACLA')
    main(location="i24")
