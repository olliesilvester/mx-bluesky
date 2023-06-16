"""
Chip manager for fixed target
This version changed to python3 March2020 by RLO
"""

import inspect
import logging
import os
import sys
import time
from pathlib import Path
from time import sleep

import numpy as np

from mx_bluesky.I24.serial import log
from mx_bluesky.I24.serial.fixed_target import i24ssx_Chip_Mapping_py3v1 as mapping
from mx_bluesky.I24.serial.fixed_target import i24ssx_Chip_StartUp_py3v1 as startup
from mx_bluesky.I24.serial.parameters.constants import (
    FULLMAP_PATH,
    LITEMAP_PATH,
    PARAM_FILE_PATH_FT,
    PVAR_FILE_PATH,
)
from mx_bluesky.I24.serial.setup_beamline import caget, caput, pv
from mx_bluesky.I24.serial.setup_beamline import setup_beamline as sup

logger = logging.getLogger("I24ssx.chip_manager")


def setup_logging():
    # Log should now change name daily.
    logfile = time.strftime("i24_%Y_%m_%d.log").lower()
    log.config(logfile)


def initialise():
    # commented out filter lines 230719 as this stage not connected
    name = inspect.stack()[0][3]
    logger.info("%s Setting VMAX VELO ACCL HHL LLM" % name)

    caput(pv.me14e_stage_x + ".VMAX", 20)
    caput(pv.me14e_stage_y + ".VMAX", 20)
    caput(pv.me14e_stage_z + ".VMAX", 20)
    # caput(pv.me14e_filter  + '.VMAX', 20)
    caput(pv.me14e_stage_x + ".VELO", 20)
    caput(pv.me14e_stage_y + ".VELO", 20)
    caput(pv.me14e_stage_z + ".VELO", 20)
    # caput(pv.me14e_filter  + '.VELO', 20)
    caput(pv.me14e_stage_x + ".ACCL", 0.01)
    caput(pv.me14e_stage_y + ".ACCL", 0.01)
    caput(pv.me14e_stage_z + ".ACCL", 0.01)
    # caput(pv.me14e_filter  + '.ACCL', 0.01)
    caput(pv.me14e_stage_x + ".HLM", 30)
    caput(pv.me14e_stage_x + ".LLM", -29)
    caput(pv.me14e_stage_y + ".HLM", 30)
    caput(pv.me14e_stage_y + ".LLM", -30)
    # caput(pv.me14e_stage_x + '.LLM', -30)
    caput(pv.me14e_stage_z + ".HLM", 5.1)
    caput(pv.me14e_stage_z + ".LLM", -4.1)
    # caput(pv.me14e_filter  + '.HLM', 45.0)
    # caput(pv.me14e_filter  + '.LLM', -45.0)
    caput(pv.me14e_gp1, 1)
    caput(pv.me14e_gp2, 0)
    caput(pv.me14e_gp3, 1)
    caput(pv.me14e_gp4, 0)
    caput(pv.me14e_filepath, "test")
    caput(pv.me14e_chip_name, "albion")
    caput(pv.me14e_dcdetdist, 1480)
    caput(pv.me14e_exptime, 0.01)
    caput(pv.me14e_pmac_str, "m508=100 m509=150")
    caput(pv.me14e_pmac_str, "m608=100 m609=150")
    caput(pv.me14e_pmac_str, "m708=100 m709=150")
    caput(pv.me14e_pmac_str, "m808=100 m809=150")

    # Define detector in use
    det_type = sup.get_detector_type()

    caput(pv.pilat_cbftemplate, 0)

    sleep(0.1)
    print("Clearing")
    logger.info("%s Clearing General Purpose PVs 1-120" % name)
    for i in range(4, 120):
        # pvar = IOC + '-MO-IOC-01:GP' + str(i)
        pvar = "ME14E-MO-IOC-01:GP" + str(i)
        caput(pvar, 0)
        sys.stdout.write(".")
        sys.stdout.flush()

    caput(pv.me14e_gp100, "press set params to read visit")
    caput(pv.me14e_gp101, det_type.name)

    print("\n", "Initialisation Complete")
    logger.info("%s Complete" % name)


def write_parameter_file(param_path: Path | str = PARAM_FILE_PATH_FT):
    name = inspect.stack()[0][3]

    if not isinstance(param_path, Path):
        param_path = Path(param_path)

    param_fid = "parameters.txt"
    logger.info("%s Writing Parameter File \n%s" % (name, param_path / param_fid))
    print("Writing Parameter File\n", param_path / param_fid)

    visit = caget(pv.me14e_gp100)

    filename = caget(pv.me14e_chip_name)

    exptime = caget(pv.me14e_exptime)
    dcdetdist = caget(pv.me14e_dcdetdist)
    protein_name = caget(pv.me14e_filepath)
    pump_repeat = caget(pv.me14e_gp4)
    pumpexptime = caget(pv.me14e_gp103)
    pumpdelay = caget(pv.me14e_gp110)
    prepumpexptime = caget(pv.me14e_gp109)
    n_exposures = caget(pv.me14e_gp3)
    map_type = caget(pv.me14e_gp2)
    chip_type = caget(pv.me14e_gp1)
    det_type = caget(pv.me14e_gp101)
    if det_type == "pilatus":
        caput(pv.pilat_cbftemplate, 0)
        numbers = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10")
        if filename.endswith(numbers):
            # Note for future reference. Appending underscore causes more hassle and
            # high probability of users accidentally overwriting data. Use a dash
            filename = filename + "-"
            print("Requested filename ends in a number. Appended dash:", filename)
            logger.info("%s Requested filename ends in a number. Appended dash")
    # historical - use chip_name instead of filename
    chip_name = filename

    # Hack for sacla3 to bismuth chip type for oxford inner
    if str(chip_type) == "3":
        chip_type = "1"

    with open(param_path / param_fid, "w") as f:
        f.write("visit \t\t%s\n" % visit)
        f.write("chip_name \t%s\n" % chip_name)
        f.write("protein_name \t%s\n" % protein_name)
        f.write("n_exposures \t%s\n" % n_exposures)
        f.write("chip_type \t%s\n" % chip_type)
        f.write("map_type \t%s\n" % map_type)
        f.write("pump_repeat \t%s\n" % pump_repeat)
        f.write("pumpexptime \t%s\n" % pumpexptime)
        f.write("pumpdelay \t%s\n" % pumpdelay)
        f.write("prepumpexptime \t%s\n" % prepumpexptime)
        f.write("exptime \t%s\n" % exptime)
        f.write("dcdetdist \t%s\n" % dcdetdist)
        f.write("det_type \t%s\n" % det_type)

    logger.info("%s visit: %s" % (name, visit))
    logger.info("%s filename: %s" % (name, chip_name))
    logger.info("%s protein_name: %s" % (name, protein_name))
    logger.info("%s n_exposures: %s" % (name, n_exposures))
    logger.info("%s chip_type: %s" % (name, chip_type))
    logger.info("%s map_type: %s" % (name, map_type))
    logger.info("%s pump_repeat: %s" % (name, pump_repeat))
    logger.info("%s pumpexptime: %s" % (name, pumpexptime))
    logger.info("%s pumpdelay: %s" % (name, pumpdelay))
    logger.info("%s prepumpexptime: %s" % (name, prepumpexptime))
    logger.info("%s detector type: %s" % (name, det_type))

    print("visit:", visit)
    print("filename:", chip_name)
    print("protein_name:", protein_name)
    print("n_exposures", n_exposures)
    print("chip_type", chip_type)
    print("map_type", map_type)
    print("pump_repeat", pump_repeat)
    print("pumpexptime", pumpexptime)
    print("pumpdelay", pumpdelay)
    print("prepumpexptime", prepumpexptime)
    print("exptime", exptime)
    print("detector", det_type)
    print("\n", "Write parameter file done", "\n")


def scrape_pvar_file(fid: str, pvar_dir: Path | str = PVAR_FILE_PATH):
    block_start_list = []
    if not isinstance(pvar_dir, Path):
        pvar_dir = Path(pvar_dir)

    with open(pvar_dir / fid, "r") as f:
        lines = f.readlines()
    for line in lines:
        line = line.rstrip()
        if line.startswith("#"):
            continue
        elif line.startswith("P3000"):
            continue
        elif line.startswith("P3011"):
            continue
        elif not len(line.split(" ")) == 2:
            continue
        else:
            entry = line.split(" ")
            block_num = entry[0][2:4]
            x = entry[0].split("=")[1]
            y = entry[1].split("=")[1]
            block_start_list.append([block_num, x, y])
    return block_start_list


def define_current_chip(chipid: str, param_path: Path | str = PVAR_FILE_PATH):
    name = inspect.stack()[0][3]
    load_stock_map("Just The First Block")
    """
    Not sure what this is for:
    print 'Setting Mapping Type to Lite'
    caput(pv.me14e_gp2, 1)
    """
    chip_type = caget(pv.me14e_gp1)
    print(chip_type, chipid)
    logger.info("%s chip_type:%s chipid:%s" % (name, chip_type, chipid))
    if chipid == "toronto":
        caput(pv.me14e_gp1, 0)
    elif chipid == "oxford":
        caput(pv.me14e_gp1, 1)

    if not isinstance(param_path, Path):
        param_path = Path(param_path)

    with open(param_path / f"{chipid}.pvar", "r") as f:
        logger.info("%s Opening %s%s.pvar" % (name, param_path, chipid))
        for line in f.readlines():
            if line.startswith("#"):
                continue
            line_from_file = line.rstrip("\n")
            print(line_from_file)
            logger.info("%s %s" % (name, line_from_file))
            caput(pv.me14e_pmac_str, line_from_file)

    print(10 * "Done ")


def save_screen_map(litemap_path: Path | str = LITEMAP_PATH):
    name = inspect.stack()[0][3]
    if not isinstance(litemap_path, Path):
        litemap_path = Path(litemap_path)

    print("\n\nSaving", litemap_path / "currentchip.map")
    logger.info("%s Saving %s currentchip.map" % (name, litemap_path))
    with open(litemap_path / "currentchip.map", "w") as f:
        print("Printing only blocks with block_val == 1")
        logger.info("%s Printing only blocks with block_val == 1" % name)
        for x in range(1, 82):
            block_str = "ME14E-MO-IOC-01:GP%i" % (x + 10)
            block_val = int(caget(block_str))
            if block_val == 1:
                print(block_str, block_val)
                logger.info("%s %s %s" % (name, block_str, block_val))
            line = "%02dstatus    P3%02d1 \t%s\n" % (x, x, block_val)
            f.write(line)
    print(10 * "Done ")
    logger.info("%s %s" % (name, 10 * "Done"))
    return 0


def upload_parameters(chipid: str, litemap_path: Path | str = LITEMAP_PATH):
    name = inspect.stack()[0][3]
    logger.info("%s Uploading Parameters to the GeoBrick" % (name))
    if chipid == "toronto":
        caput(pv.me14e_gp1, 0)
        width = 9
    elif chipid == "oxford":
        caput(pv.me14e_gp1, 1)
        width = 8
    if not isinstance(litemap_path, Path):
        litemap_path = Path(litemap_path)

    with open(litemap_path / "currentchip.map", "r") as f:
        print("chipid", chipid)
        print(width)
        logger.info("%s chipid %s" % (name, chipid))
        logger.info("%s width %s" % (name, width))
        x = 1
        for line in f.readlines()[: width**2]:
            cols = line.split()
            pvar = cols[1]
            value = cols[2]
            s = pvar + "=" + value
            if value != "1":
                s2 = pvar + "   "
                sys.stdout.write(s2)
            else:
                sys.stdout.write(s + " ")
            sys.stdout.flush()
            if x == width:
                print()
                x = 1
            else:
                x += 1
            caput(pv.me14e_pmac_str, s)
            sleep(0.02)

    logger.warning("%s Automatic Setting Mapping Type to Lite has been disabled" % name)
    print(10 * "Done ")
    logger.info("%s %s" % (name, 10 * "Done"))


def upload_full(fullmap_path: Path | str = FULLMAP_PATH):
    name = inspect.stack()[0][3]
    if not isinstance(fullmap_path, Path):
        fullmap_path = Path(fullmap_path)

    with open(fullmap_path / "currentchip.full", "r") as fh:
        f = fh.readlines()

    for _ in range(len(f) // 2):
        pmac_list = []
        for _ in range(2):
            pmac_list.append(f.pop(0).rstrip("\n"))
        writeline = " ".join(pmac_list)
        print(writeline)
        logger.info("%s %s" % (name, writeline))
        caput(pv.me14e_pmac_str, writeline)
        sleep(0.02)

    print(10 * "Done ")
    logger.info("%s %s" % (name, 10 * "Done"))


def load_stock_map(map_choice):
    name = inspect.stack()[0][3]
    logger.info("%s Adjusting Lite Map EDM Screen" % name)
    print("Please wait, adjusting lite map")
    #
    r33 = [19, 18, 17, 26, 31, 32, 33, 24, 25]
    r55 = [9, 10, 11, 12, 13, 16, 27, 30, 41, 40, 39, 38, 37, 34, 23, 20] + r33
    r77 = [
        7,
        6,
        5,
        4,
        3,
        2,
        1,
        14,
        15,
        28,
        29,
        42,
        43,
        44,
        45,
        46,
        47,
        48,
        49,
        36,
        35,
        22,
        21,
        8,
    ] + r55
    #
    h33 = [3, 2, 1, 6, 7, 8, 9, 4, 5]
    x33 = [31, 32, 33, 40, 51, 50, 49, 42, 41]
    x55 = [25, 24, 23, 22, 21, 34, 39, 52, 57, 58, 59, 60, 61, 48, 43, 30] + x33
    x77 = [
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        20,
        35,
        38,
        53,
        56,
        71,
        70,
        69,
        68,
        67,
        66,
        65,
        62,
        47,
        44,
        29,
        26,
    ] + x55
    x99 = [
        9,
        8,
        7,
        6,
        5,
        4,
        3,
        2,
        1,
        18,
        19,
        36,
        37,
        54,
        55,
        72,
        73,
        74,
        75,
        76,
        77,
        78,
        79,
        80,
        81,
        64,
        63,
        46,
        45,
        28,
        27,
        10,
    ] + x77
    x44 = [22, 21, 20, 19, 30, 35, 46, 45, 44, 43, 38, 27, 28, 29, 36, 37]
    x49 = [x + 1 for x in range(49)]
    x66 = [
        10,
        11,
        12,
        13,
        14,
        15,
        18,
        31,
        34,
        47,
        50,
        51,
        52,
        53,
        54,
        55,
        42,
        39,
        26,
        23,
    ] + x44
    x88 = [
        8,
        7,
        6,
        5,
        4,
        3,
        2,
        1,
        16,
        17,
        32,
        33,
        48,
        49,
        64,
        63,
        62,
        61,
        60,
        59,
        58,
        57,
        56,
        41,
        40,
        25,
        24,
        9,
    ] + x66
    #
    # Columns for doing half chips
    c1 = [1, 2, 3, 4, 5, 6, 7, 8]
    c2 = [9, 10, 11, 12, 13, 14, 15, 16]
    c3 = [17, 18, 19, 20, 21, 22, 23, 24]
    c4 = [25, 26, 27, 28, 29, 30, 31, 32]
    c5 = [33, 34, 35, 36, 37, 38, 39, 40]
    c6 = [41, 42, 43, 44, 45, 46, 47, 48]
    c7 = [49, 50, 51, 52, 53, 54, 55, 56]
    c8 = [57, 58, 59, 60, 61, 62, 63, 64]
    half1 = c1 + c2 + c3 + c4
    half2 = c5 + c6 + c7 + c8

    map_dict = {}
    map_dict["Just The First Block"] = [1]
    map_dict["clear"] = []
    #
    map_dict["r33"] = r33
    map_dict["r55"] = r55
    map_dict["r77"] = r77
    #
    map_dict["h33"] = h33
    #
    map_dict["x33"] = x33
    map_dict["x44"] = x44
    map_dict["x49"] = x49
    map_dict["x55"] = x55
    map_dict["x66"] = x66
    map_dict["x77"] = x77
    map_dict["x88"] = x88
    map_dict["x99"] = x99

    map_dict["half1"] = half1
    map_dict["half2"] = half2

    print("Clearing")
    logger.info("%s Clearing GP 10-74" % name)
    for i in range(1, 65):
        pvar = "ME14E-MO-IOC-01:GP" + str(i + 10)
        caput(pvar, 0)
        sys.stdout.write(".")
        sys.stdout.flush()
    print("\nMap cleared")
    logger.info("%s Cleared Map" % name)
    print("Loading map_choice", map_choice)
    logger.info("%s Loading Map Choice %s" % (name, map_choice))
    for i in map_dict[map_choice]:
        pvar = "ME14E-MO-IOC-01:GP" + str(i + 10)
        caput(pvar, 1)
    print(10 * "Done ")


def load_lite_map(litemap_path: Path | str = LITEMAP_PATH):
    name = inspect.stack()[0][3]
    load_stock_map("clear")
    # fmt: off
    toronto_block_dict = {
        'A1': '01', 'A2': '02', 'A3': '03', 'A4': '04', 'A5': '05', 'A6': '06', 'A7': '07', 'A8': '08', 'A9': '09',
        'B1': '18', 'B2': '17', 'B3': '16', 'B4': '15', 'B5': '14', 'B6': '13', 'B7': '12', 'B8': '11', 'B9': '10',
        'C1': '19', 'C2': '20', 'C3': '21', 'C4': '22', 'C5': '23', 'C6': '24', 'C7': '25', 'C8': '26', 'C9': '27',
        'D1': '36', 'D2': '35', 'D3': '34', 'D4': '33', 'D5': '32', 'D6': '31', 'D7': '30', 'D8': '29', 'D9': '28',
        'E1': '37', 'E2': '38', 'E3': '39', 'E4': '40', 'E5': '41', 'E6': '42', 'E7': '43', 'E8': '44', 'E9': '45',
        'F1': '54', 'F2': '53', 'F3': '52', 'F4': '51', 'F5': '50', 'F6': '49', 'F7': '48', 'F8': '47', 'F9': '46',
        'G1': '55', 'G2': '56', 'G3': '57', 'G4': '58', 'G5': '59', 'G6': '60', 'G7': '61', 'G8': '62', 'G9': '63',
        'H1': '72', 'H2': '71', 'H3': '70', 'H4': '69', 'H5': '68', 'H6': '67', 'H7': '66', 'H8': '65', 'H9': '64',
        'I1': '73', 'I2': '74', 'I3': '75', 'I4': '76', 'I5': '77', 'I6': '78', 'I7': '79', 'I8': '80', 'I9': '81',
    }
    # Oxford_block_dict is wrong (columns and rows need to flip) added in script below to generate it automatically however kept this for backwards compatiability/reference
    oxford_block_dict = {   # noqa: F841
        'A1': '01', 'A2': '02', 'A3': '03', 'A4': '04', 'A5': '05', 'A6': '06', 'A7': '07', 'A8': '08',
        'B1': '16', 'B2': '15', 'B3': '14', 'B4': '13', 'B5': '12', 'B6': '11', 'B7': '10', 'B8': '09',
        'C1': '17', 'C2': '18', 'C3': '19', 'C4': '20', 'C5': '21', 'C6': '22', 'C7': '23', 'C8': '24',
        'D1': '32', 'D2': '31', 'D3': '30', 'D4': '29', 'D5': '28', 'D6': '27', 'D7': '26', 'D8': '25',
        'E1': '33', 'E2': '34', 'E3': '35', 'E4': '36', 'E5': '37', 'E6': '38', 'E7': '39', 'E8': '40',
        'F1': '48', 'F2': '47', 'F3': '46', 'F4': '45', 'F5': '44', 'F6': '43', 'F7': '42', 'F8': '41',
        'G1': '49', 'G2': '50', 'G3': '51', 'G4': '52', 'G5': '53', 'G6': '54', 'G7': '55', 'G8': '56',
        'H1': '64', 'H2': '63', 'H3': '62', 'H4': '61', 'H5': '60', 'H6': '59', 'H7': '58', 'H8': '57',
    }
    # fmt: on
    chip_type = caget(pv.me14e_gp1)
    if chip_type == 0:
        logger.info("%s Toronto Block Order" % name)
        print("Toronto Block Order")
        block_dict = toronto_block_dict
    elif chip_type == 1 or chip_type == 3 or chip_type == 10:
        logger.info("%s Oxford Block Order" % name)
        print("Oxford Block Order")
        # block_dict = oxford_block_dict
        rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
        columns = list(range(1, 10))
        btn_names = {}
        flip = True
        for x, column in enumerate(columns):
            for y, row in enumerate(rows):
                i = x * 8 + y
                if i % 8 == 0 and flip is False:
                    flip = True
                    z = 8 - (y + 1)
                elif i % 8 == 0 and flip is True:
                    flip = False
                    z = y
                elif flip is False:
                    z = y
                elif flip is True:
                    z = 8 - (y + 1)
                else:
                    logger.warning("%s Problem in Chip Grid Creation" % name)
                    print("something is wrong with chip grid creation")
                    break
                button_name = str(row) + str(column)
                lab_num = x * 8 + z
                label = "%02.d" % (lab_num + 1)
                btn_names[button_name] = label
                # print button_name, btn_names[button_name]
        block_dict = btn_names

    if not isinstance(litemap_path, Path):
        litemap_path = Path(litemap_path)

    litemap_fid = str(caget(pv.me14e_gp5)) + ".lite"
    print("Please wait, loading LITE map")
    print("Opening", litemap_path / litemap_fid)
    logger.info("%s Loading Lite Map" % name)
    logger.info("%s Opening %s" % (name, litemap_path / litemap_fid))
    with open(litemap_path / litemap_fid, "r") as fh:
        f = fh.readlines()
    for line in f:
        entry = line.split()
        block_name = entry[0]
        yesno = entry[1]
        block_num = block_dict[block_name]
        pvar = "ME14E-MO-IOC-01:GP" + str(int(block_num) + 10)
        logger.info("%s %s %s %s" % (name, block_name, yesno, pvar))
        print(block_name, yesno, pvar)
        caput(pvar, yesno)
    print(10 * "Done ")


def load_full_map(location: str = "SACLA", fullmap_path: Path | str = FULLMAP_PATH):
    name = inspect.stack()[0][3]
    if location == "i24":
        (
            chip_name,
            visit,
            sub_dir,
            n_exposures,
            chip_type,
            map_type,
        ) = startup.scrape_parameter_file(location)
    else:
        (
            chip_name,
            sub_dir,
            n_exposures,
            chip_type,
            map_type,
        ) = startup.scrape_parameter_file(location)
    if not isinstance(fullmap_path, Path):
        fullmap_path = Path(fullmap_path)

    fullmap_fid = fullmap_path / f"{str(caget(pv.me14e_gp5))}.spec"
    print("opening", fullmap_fid)
    logger.info("%s opening %s" % (name, fullmap_fid))
    mapping.plot_file(fullmap_fid, chip_type)
    print("\n\n", 10 * "PNG ")
    mapping.convert_chip_to_hex(fullmap_fid, chip_type)
    os.system(
        "cp %s %s"
        % (fullmap_fid.with_suffix(".full"), fullmap_path / "currentchip.full")
    )
    logger.info(
        "%s cp %s %s"
        % (name, fullmap_fid.with_suffix(".full"), fullmap_path / "currentchip.full")
    )
    print(10 * "Done ", "\n")


def moveto(place):
    name = inspect.stack()[0][3]
    logger.info("%s Move to %s" % (name, place))
    print(5 * (place + " "))
    chip_type = int(caget(pv.me14e_gp1))
    print("CHIP TYPE", chip_type)
    if chip_type == 0:
        print("Toronto Move")
        logger.info("%s Toronto Move" % (name))
        if place == "origin":
            caput(pv.me14e_stage_x, 0.0)
            caput(pv.me14e_stage_y, 0.0)
        if place == "f1":
            caput(pv.me14e_stage_x, +18.975)
            caput(pv.me14e_stage_y, 0.0)
        if place == "f2":
            caput(pv.me14e_stage_x, 0.0)
            caput(pv.me14e_stage_y, +21.375)

    elif chip_type == 1:
        print("Oxford Move")
        logger.info("%s Oxford Move" % (name))
        if place == "origin":
            caput(pv.me14e_stage_x, 0.0)
            caput(pv.me14e_stage_y, 0.0)
        if place == "f1":
            caput(pv.me14e_stage_x, 25.40)
            caput(pv.me14e_stage_y, 0.0)
        if place == "f2":
            caput(pv.me14e_stage_x, 0.0)
            caput(pv.me14e_stage_y, 25.40)

    elif chip_type == 3:
        print("Oxford Inner Move")
        logger.info("%s Oxford Inner Move" % (name))
        if place == "origin":
            caput(pv.me14e_stage_x, 0.0)
            caput(pv.me14e_stage_y, 0.0)
        if place == "f1":
            caput(pv.me14e_stage_x, 24.60)
            caput(pv.me14e_stage_y, 0.0)
        if place == "f2":
            caput(pv.me14e_stage_x, 0.0)
            caput(pv.me14e_stage_y, 24.60)

    elif chip_type == 6:
        print("Custom Move")
        logger.info("%s Custom Chip Move" % (name))
        if place == "origin":
            caput(pv.me14e_stage_x, 0.0)
            caput(pv.me14e_stage_y, 0.0)
        if place == "f1":
            caput(pv.me14e_stage_x, 25.40)
            caput(pv.me14e_stage_y, 0.0)
        if place == "f2":
            caput(pv.me14e_stage_x, 0.0)
            caput(pv.me14e_stage_y, 25.40)

    elif chip_type == 10:
        print("Oxford 6 by 6 blocks Move")
        logger.info("%s Oxford 6 by 6 blocks Move" % (name))
        if place == "origin":
            caput(pv.me14e_stage_x, 0.0)
            caput(pv.me14e_stage_y, 0.0)
        if place == "f1":
            caput(pv.me14e_stage_x, 18.25)
            caput(pv.me14e_stage_y, 0.0)
        if place == "f2":
            caput(pv.me14e_stage_x, 0.0)
            caput(pv.me14e_stage_y, 18.25)

    else:
        print("Unknown chip_type move")
        logger.warning("%s Unknown chip_type move" % name)

    # Non Chip Specific Move
    if place == "zero":
        logger.info("%s moving to %s" % (name, place))
        caput(pv.me14e_pmac_str, "!x0y0z0")

    elif place == "yag":
        logger.info("%s moving %s" % (name, place))
        caput(pv.me14e_stage_x, 1.0)
        caput(pv.me14e_stage_y, 1.0)
        caput(pv.me14e_stage_z, 1.0)

    elif place == "load_position":
        print("load position")
        logger.info("%s %s" % (name, place))
        # caput(pv.me14e_filter, 20)
        # caput(pv.me14e_stage_x, -15.0)
        # caput(pv.me14e_stage_y, 25.0)
        # caput(pv.me14e_stage_z, 0.0)
        # caput(pv.me14e_pmac_str, 'M512=0 M511=1')
        # i24 settings
        caput(pv.bs_mp_select, "Robot")
        caput(pv.bl_mp_select, "Out")
        # caput(pv.aptr1_mp_select, 'Robot')
        # reduced detz while stage problems. was 1480
        caput(pv.det_z, 1300)

    elif place == "collect_position":
        print("collect position")
        logger.info("%s %s" % (name, place))
        caput(pv.me14e_filter, 20)
        caput(pv.me14e_stage_x, 0.0)
        caput(pv.me14e_stage_y, 0.0)
        caput(pv.me14e_stage_z, 0.0)
        # caput(pv.me14e_pmac_str, 'M512=0 M511=1')
        caput(pv.bs_mp_select, "Data Collection")
        # caput(pv.aptr1_mp_select, 'In')
        caput(pv.bl_mp_select, "In")

    elif place == "microdrop_position":
        print("microdrop align position")
        logger.info("%s %s" % (name, place))
        # caput(pv.me14e_filter, 20)
        caput(pv.me14e_stage_x, 6.0)
        caput(pv.me14e_stage_y, -7.8)
        caput(pv.me14e_stage_z, 0.0)
        # caput(pv.me14e_pmac_str, 'M512=0 M511=1')
        # caput(pv.bs_mp_select, 'Data Collection')
        # caput(pv.aptr1_mp_select, 'In')
        # caput(pv.bl_mp_select, 'In')

    elif place == "lightin":
        print("light in")
        logger.info("%s Light In" % (name))
        caput(pv.me14e_filter, 24)

    elif place == "lightout":
        print("light out")
        logger.info("%s Light Out" % (name))
        caput(pv.me14e_filter, -24)

    elif place == "flipperin":
        print("flipper in")
        logger.info("%s Flipper In" % (name))
        logger.debug("%s nb need M508=100 M509 =150 somewhere" % name)
        # nb need M508=100 M509 =150 somewhere
        caput(pv.me14e_pmac_str, "M512=0 M511=1")

    elif place == "flipperout":
        print("flipper out")
        logger.info("%s Flipper out" % (name))
        caput(pv.me14e_pmac_str, " M512=1 M511=1")

    elif place == "laser1on":
        print("Laser 1 /BNC2 shutter is open")
        # Use M712 = 0 if triggering on falling edge. M712 =1 if on rising edge
        # Be sure to also change laser1off
        # caput(pv.me14e_pmac_str, ' M712=0 M711=1')
        caput(pv.me14e_pmac_str, " M712=1 M711=1")

    elif place == "laser1off":
        print("Laser 1 shutter is closed")
        caput(pv.me14e_pmac_str, " M712=0 M711=1")

    elif place == "laser2on":
        print("Laser 2 / BNC3 shutter is open")
        caput(pv.me14e_pmac_str, " M812=1 M811=1")

    elif place == "laser2off":
        print("Laser 2 shutter is closed")
        caput(pv.me14e_pmac_str, " M812=0 M811=1")

    elif place == "laser1burn":
        led_burn_time = caget(pv.me14e_gp103)
        print("Laser 1  on")
        print("Burn time is", led_burn_time, "s")
        logger.info("Laser 1 on")
        logger.info("burntime %s s" % (led_burn_time))
        caput(pv.me14e_pmac_str, " M712=1 M711=1")
        sleep(int(float(led_burn_time)))
        print("Laser 1 off")
        logger.info("Laser 1 off")
        caput(pv.me14e_pmac_str, " M712=0 M711=1")

    elif place == "laser2burn":
        led_burn_time = caget(pv.me14e_gp109)
        print("Laser 2 on")
        print("Burn time is", led_burn_time, "s")
        logger.info("Laser 2 on")
        logger.info("burntime %s s" % (led_burn_time))
        caput(pv.me14e_pmac_str, " M812=1 M811=1")
        sleep(int(float(led_burn_time)))
        print("laser 2 off")
        logger.info("Laser 2 off")
        caput(pv.me14e_pmac_str, " M812=0 M811=1")


def scrape_mtr_directions():
    name = inspect.stack()[0][3]
    param_path = "/dls_sw/i24/scripts/fastchips/parameter_files/"
    # param_path = '/localhome/local/Documents/sacla/parameter_files/'
    with open(param_path + "motor_direction.txt", "r") as f:
        lines = f.readlines()
    mtr1_dir, mtr2_dir, mtr3_dir = 1, 1, 1
    for line in lines:
        if line.startswith("mtr1"):
            mtr1_dir = float(int(line.split("=")[1]))
        elif line.startswith("mtr2"):
            mtr2_dir = float(int(line.split("=")[1]))
        elif line.startswith("mtr3"):
            mtr3_dir = float(int(line.split("=")[1]))
        else:
            continue
    logger.info(
        "%s mt1_dir %s mtr2_dir %s mtr3_dir %s" % (name, mtr1_dir, mtr2_dir, mtr3_dir)
    )
    return mtr1_dir, mtr2_dir, mtr3_dir


def fiducial(point):
    name = inspect.stack()[0][3]
    scale = 10000.0  # noqa: F841
    param_path = "/dls_sw/i24/scripts/fastchips/parameter_files/"
    # param_path = '/localhome/local/Documents/sacla/parameter_files/'

    mtr1_dir, mtr2_dir, mtr3_dir = scrape_mtr_directions()

    rbv_1 = float(caget(pv.me14e_stage_x + ".RBV"))
    rbv_2 = float(caget(pv.me14e_stage_y + ".RBV"))
    rbv_3 = float(caget(pv.me14e_stage_z + ".RBV"))

    print("rbv1", rbv_1)
    raw_1 = float(caget(pv.me14e_stage_x + ".RRBV"))
    raw_2 = float(caget(pv.me14e_stage_y + ".RRBV"))
    raw_3 = float(caget(pv.me14e_stage_z + ".RRBV"))

    f_x = rbv_1
    f_y = rbv_2
    f_z = rbv_3

    print("\nWriting Fiducial File", 20 * ("%s " % point))
    print("MTR\tRBV\tRAW\tDirect.\tf_value")
    print("MTR1\t%1.4f\t%i\t%i\t%1.4f" % (rbv_1, raw_1, mtr1_dir, f_x))
    print("MTR2\t%1.4f\t%i\t%i\t%1.4f" % (rbv_2, raw_2, mtr2_dir, f_y))
    print("MTR3\t%1.4f\t%i\t%i\t%1.4f" % (rbv_3, raw_3, mtr3_dir, f_z))
    print("Writing Fiducial File", 20 * ("%s " % point))

    logger.info(
        "%s Writing Fiducial File %sfiducial_%s.txt" % (name, param_path, point)
    )
    logger.info("%s MTR\tRBV\tRAW\tCorr\tf_value" % (name))
    logger.info("%s MTR1\t%1.4f\t%i\t%i\t%1.4f" % (name, rbv_1, raw_1, mtr1_dir, f_x))
    logger.info("%s MTR2\t%1.4f\t%i\t%i\t%1.4f" % (name, rbv_2, raw_2, mtr2_dir, f_y))
    logger.info("%s MTR3\t%1.4f\t%i\t%i\t%1.4f" % (name, rbv_3, raw_3, mtr3_dir, f_y))

    with open(param_path + "fiducial_%s.txt" % point, "w") as f:
        f.write("MTR\tRBV\tRAW\tCorr\tf_value\n")
        f.write("MTR1\t%1.4f\t%i\t%i\t%1.4f\n" % (rbv_1, raw_1, mtr1_dir, f_x))
        f.write("MTR2\t%1.4f\t%i\t%i\t%1.4f\n" % (rbv_2, raw_2, mtr2_dir, f_y))
        f.write("MTR3\t%1.4f\t%i\t%i\t%1.4f" % (rbv_3, raw_3, mtr3_dir, f_z))
    print(10 * "Done ")


def scrape_mtr_fiducials(point):
    param_path = "/dls_sw/i24/scripts/fastchips/parameter_files/"
    # param_path = '/localhome/local/Documents/sacla/parameter_files/'
    with open(param_path + "fiducial_%i.txt" % point, "r") as f:
        f_lines = f.readlines()[1:]
    f_x = float(f_lines[0].rsplit()[4])
    f_y = float(f_lines[1].rsplit()[4])
    f_z = float(f_lines[2].rsplit()[4])
    return f_x, f_y, f_z


def cs_maker():
    name = inspect.stack()[0][3]
    chip_type = int(caget(pv.me14e_gp1))
    fiducial_dict = {}
    fiducial_dict[0] = [18.975, 21.375]
    fiducial_dict[1] = [25.400, 25.400]
    fiducial_dict[2] = [24.968, 24.968]
    fiducial_dict[3] = [24.600, 24.600]
    fiducial_dict[4] = [27.500, 27.500]
    fiducial_dict[5] = [17.175, 17.175]
    fiducial_dict[6] = [25.400, 25.400]
    fiducial_dict[7] = [19.135, 9.635]
    fiducial_dict[8] = [19.525, 9.335]
    fiducial_dict[9] = [2.375, 2.375]
    fiducial_dict[10] = [18.25, 18.25]
    print(chip_type, fiducial_dict[chip_type])
    logger.info(
        "%s chip type is %s with size %s" % (name, chip_type, fiducial_dict[chip_type])
    )

    mtr1_dir, mtr2_dir, mtr3_dir = scrape_mtr_directions()
    f1_x, f1_y, f1_z = scrape_mtr_fiducials(1)
    f2_x, f2_y, f2_z = scrape_mtr_fiducials(2)
    print("mtr1 direction", mtr1_dir)
    print("mtr2 direction", mtr2_dir)
    print("mtr3 direction", mtr3_dir)

    """
    Theory
    Rx: rotation about X-axis, pitch
    Ry: rotation about Y-axis, yaw
    Rz: rotation about Z-axis, roll
    The order of rotation is Roll->Yaw->Pitch (Rx*Ry*Rz)
    Rx           Ry          Rz
    |1  0   0| | Cy  0 Sy| |Cz -Sz 0|   | CyCz        -CxSz         Sy  |
    |0 Cx -Sx|*|  0  1  0|*|Sz  Cz 0| = | SxSyCz+CxSz -SxSySz+CxCz -SxCy|
    |0 Sx  Cx| |-Sy  0 Cy| | 0   0 1|   |-CxSyCz+SxSz  CxSySz+SxCz  CxCy|

    BELOW iS TEST TEST (CLOCKWISE)
    Rx           Ry          Rz
    |1  0   0| | Cy 0 -Sy| |Cz  Sz 0|   | CyCz         CxSz         -Sy  |
    |0 Cx  Sx|*|  0  1  0|*|-Sz Cz 0| = | SxSyCz-CxSz  SxSySz+CxCz  SxCy|
    |0 -Sx Cx| | Sy  0 Cy| | 0   0 1|   | CxSyCz+SxSz  CxSySz-SxCz  CxCy|

    """
    # Rotation Around Z #
    # If stages upsidedown (I24) change sign of Sz
    # Sz1 =       f1_y / fiducial_dict[chip_type][0]
    Sz1 = -1 * f1_y / fiducial_dict[chip_type][0]
    # Sz2 = -1 * (f2_x / fiducial_dict[chip_type][1])
    Sz2 = f2_x / fiducial_dict[chip_type][1]
    Sz = -1 * ((Sz1 + Sz2) / 2)
    Cz = np.sqrt((1 - Sz**2))
    print("Sz1 , %1.4f, %1.4f" % (Sz1, np.degrees(np.arcsin(Sz1))))
    logger.info("%s Sz1 , %1.4f, %1.4f" % (name, Sz1, np.degrees(np.arcsin(Sz1))))
    print("Sz2 , %1.4f, %1.4f" % (Sz2, np.degrees(np.arcsin(Sz2))))
    logger.info("%s Sz2 , %1.4f, %1.4f" % (name, Sz2, np.degrees(np.arcsin(Sz2))))
    print("Sz ,  %1.4f, %1.4f" % (Sz, np.degrees(np.arcsin(Sz))))
    logger.info("%s Sz , %1.4f, %1.4f" % (name, Sz, np.degrees(np.arcsin(Sz))))
    print("Cz ,  %1.4f, %1.4f\n" % (Cz, np.degrees(np.arccos(Cz))))
    logger.info("%s Cz , %1.4f, %1.4f" % (name, Cz, np.degrees(np.arcsin(Cz))))
    # Rotation Around Y #
    # Sy = f1_z /  fiducial_dict[chip_type][0]
    Sy = 1 * f1_z / fiducial_dict[chip_type][0]
    Cy = np.sqrt((1 - Sy**2))
    print("Sy , %1.4f, %1.4f" % (Sy, np.degrees(np.arcsin(Sy))))
    logger.info("%s Sy , %1.4f, %1.4f" % (name, Sy, np.degrees(np.arcsin(Sy))))
    print("Cy , %1.4f, %1.4f\n" % (Cy, np.degrees(np.arccos(Cy))))
    logger.info("%s Cy , %1.4f, %1.4f" % (name, Cy, np.degrees(np.arcsin(Cy))))
    # Rotation Around X #
    # If stages upsidedown (I24) change sign of Sx
    Sx = -1 * f2_z / fiducial_dict[chip_type][1]
    # Sx =  f2_z /  fiducial_dict[chip_type][1]
    Cx = np.sqrt((1 - Sx**2))
    print("Sx , %1.4f, %1.4f" % (Sx, np.degrees(np.arcsin(Sx))))
    logger.info("%s Sx , %1.4f, %1.4f" % (name, Sx, np.degrees(np.arcsin(Sx))))
    print("Cx , %1.4f, %1.4f\n" % (Cx, np.degrees(np.arccos(Cx))))
    logger.info("%s Cx , %1.4f, %1.4f" % (name, Cx, np.degrees(np.arcsin(Cx))))

    # Crucifix 1:   In normal orientation on I24 4 oct 2022
    scalex, scaley, scalez = 10018.0, 9999.5, 10000.0
    # Crucifix 1:   In beamline position (upside down facing away)
    # X=0.000099896 , Y=0.000099983, Z=0.0001000 (mm/cts for MRES and ERES)
    # pre-sacla3 scalex, scaley, scalez  = 10010.4, 10001.7, 10000.0
    # Crucifix 2:   In normal orientation from SACLA4
    # scalex, scaley, scalez  = 10011.4, 10000.0, 10000.0
    # Crucifix 2:   Upside down on beamline April 2018
    # scalex, scaley, scalez  = 10008.4, 10003.0, 10000.0
    # Crucifix 2:   Dismantled on beamline Sept 2022
    # scalex, scaley, scalez  = 10021.5, 10006.7, 10000.0
    # Crucifix 2:   In normal orientation (sat on table facing away)
    # X=0.0000999 , Y=0.00009996, Z=0.0001000 (mm/cts for MRES and ERES)
    # scalex,scaley,scalez  = 10010.0, 10004.0, 10000.0
    # Temple 1:   In normal orientation (sat on table facing away)
    # X=0.0000 , Y=0.0000, Z=0.0001000 (mm/cts for MRES and ERES)
    # scalex,scaley,scalez  = 10008.0, 10002.0, 10000.0

    # minus signs added Aug17 in lab 30 preparing for sacla
    # added to y1factor x2factor
    x1factor = mtr1_dir * scalex * (Cy * Cz)
    y1factor = mtr2_dir * scaley * (-1.0 * Cx * Sz)
    z1factor = mtr3_dir * scalez * Sy

    x2factor = mtr1_dir * scalex * ((Sx * Sy * Cz) + (Cx * Sz))
    y2factor = mtr2_dir * scaley * ((Cx * Cz) - (Sx * Sy * Sz))
    z2factor = mtr3_dir * scalez * (-1.0 * Sx * Cy)

    x3factor = mtr1_dir * scalex * ((Sx * Sz) - (Cx * Sy * Cz))
    y3factor = mtr2_dir * scaley * ((Cx * Sy * Sz) + (Sx * Cz))
    z3factor = mtr3_dir * scalez * (Cx * Cy)
    """
    Rx           Ry          Rz
    |1  0   0| | Cy  0 Sy| |Cz -Sz 0|   | CyCz        -CxSz         Sy  |
    |0 Cx -Sx|*|  0  1  0|*|Sz  Cz 0| = | SxSyCz+CxSz -SxSySz+CxCz -SxCy|
    |0 Sx  Cx| |-Sy  0 Cy| | 0   0 1|   |-CxSyCz+SxSz  CxSySz+SxCz  CxCy|
    """
    # skew is the difference between the Sz1 and Sz2 after rotation is taken out.
    # this should be measured in situ prior to expriment
    # In situ is measure by hand using opposite and adjacent RBV after calibration of
    # scale factors
    # print 10*'WARNING\n', '\nHave you calculated skew?\n\n', 10*'WARNING\n'
    # Crucifix 1 on beamline
    # skew = 0.0126
    # Crucifix 2 deconstructed on beamline
    skew = -0.189
    # skew = -1.2734
    # Crucifix 3
    # skew = 0.0883
    # Temple 1
    # skew = 0.02

    print("Skew being used is: %1.4f" % skew)
    logger.info("%s Skew being used is: %1.4f" % (name, skew))
    s1 = np.degrees(np.arcsin(Sz1))
    s2 = np.degrees(np.arcsin(Sz2))
    rot = np.degrees(np.arcsin((Sz1 + Sz2) / 2))
    calc_skew = (s1 - rot) - (s2 - rot)
    print("s1:%1.4f s2:%1.4f rot:%1.4f" % (s1, s2, rot))
    logger.info("%s s1:%1.4f s2:%1.4f rot:%1.4f" % (name, s1, s2, rot))
    print("Calculated rotation from current fiducials is: %1.4f" % rot)
    logger.info("%s Calculated rotation from current fiducials is: %1.4f" % (name, rot))
    print("Calculated skew from current fiducials is: %1.4f" % calc_skew)
    logger.info(
        "%s Calculated Skew from current fiducials is: %1.4f" % (name, calc_skew)
    )
    print("Calculated skew has been known to have the wrong sign")
    logger.info("%s Calculated Skew has been known to have the wrong sign")

    # skew = calc_skew
    sinD = np.sin((skew / 2) * (np.pi / 180))
    cosD = np.cos((skew / 2) * (np.pi / 180))
    new_x1factor = (x1factor * cosD) + (y1factor * sinD)
    new_y1factor = (x1factor * sinD) + (y1factor * cosD)
    new_x2factor = (x2factor * cosD) + (y2factor * sinD)
    new_y2factor = (x2factor * sinD) + (y2factor * cosD)

    cs1 = "#1->%+1.3fX%+1.3fY%+1.3fZ" % (new_x1factor, new_y1factor, z1factor)
    cs2 = "#2->%+1.3fX%+1.3fY%+1.3fZ" % (new_x2factor, new_y2factor, z2factor)
    cs3 = "#3->%+1.3fX%+1.3fY%+1.3fZ" % (x3factor, y3factor, z3factor)
    print("\n".join([cs1, cs2, cs3]))
    logger.info("%s %s" % (name, "\n".join([cs1, cs2, cs3])))
    print(
        "These should be 1. This is the sum of the squares of the factors divided by their scale"
    )
    logger.info(
        "%s These should be 1. This is the sum of the squares of the factors divided by their scale"
        % (name)
    )
    sqfact1 = np.sqrt(x1factor**2 + y1factor**2 + z1factor**2) / scalex
    sqfact2 = np.sqrt(x2factor**2 + y2factor**2 + z2factor**2) / scaley
    sqfact3 = np.sqrt(x3factor**2 + y3factor**2 + z3factor**2) / scalez
    print(sqfact1)
    print(sqfact2)
    print(sqfact3)
    logger.info("%s %1.4f \n %1.4f \n %1.4f" % (name, sqfact1, sqfact2, sqfact3))
    print("Long wait, please be patient")
    logger.info("%s Long wait, please be patient" % (name))
    caput(pv.me14e_pmac_str, "!x0y0z0")
    sleep(2.5)
    caput(pv.me14e_pmac_str, "&2")
    caput(pv.me14e_pmac_str, cs1)
    caput(pv.me14e_pmac_str, cs2)
    caput(pv.me14e_pmac_str, cs3)
    caput(pv.me14e_pmac_str, "!x0y0z0")
    sleep(0.1)
    caput(pv.me14e_pmac_str, "#1hmz#2hmz#3hmz")
    sleep(0.1)
    print(5 * "chip_type", type(chip_type))
    logger.info("%s Chip_type is %s" % (name, chip_type))
    # NEXT THREE LINES COMMENTED OUT FOR CS TESTS 5 JUNE
    if str(chip_type) == "1":
        caput(pv.me14e_pmac_str, "!x0.4y0.4")
        sleep(0.1)
        caput(pv.me14e_pmac_str, "#1hmz#2hmz#3hmz")
        print(10 * "CSDone ")
    else:
        caput(pv.me14e_pmac_str, "#1hmz#2hmz#3hmz")
        print(10 * "CSDone ")


def cs_reset():
    cs1 = "#1->-10000X+0Y+0Z"
    cs2 = "#2->+0X+10000Y+0Z"
    cs3 = "#3->0X+0Y+10000Z"
    strg = "\n".join([cs1, cs2, cs3])
    print(strg)
    caput(pv.me14e_pmac_str, "&2")
    sleep(0.5)
    caput(pv.me14e_pmac_str, cs1)
    sleep(0.5)
    caput(pv.me14e_pmac_str, cs2)
    sleep(0.5)
    caput(pv.me14e_pmac_str, cs3)
    print(10 * "CSDone ")


def pumpprobe_calc():
    exptime = float(caget(pv.me14e_exptime))
    pumpexptime = float(caget(pv.me14e_gp103))
    movetime = 0.008
    print("X-ray exposure time", exptime)
    print("Laser dwell time", pumpexptime)
    repeat1 = 2 * 20 * (movetime + (pumpexptime + exptime) / 2)
    repeat2 = 4 * 20 * (movetime + (pumpexptime + exptime) / 2)
    repeat3 = 6 * 20 * (movetime + (pumpexptime + exptime) / 2)
    repeat5 = 10 * 20 * (movetime + (pumpexptime + exptime) / 2)
    repeat10 = 20 * 20 * (movetime + (pumpexptime + exptime) / 2)
    print("repeat1:", round(repeat1, 4), "s")
    print("repeat2:", round(repeat2, 4), "s")
    print("repeat3:", round(repeat3, 4), "s")
    print("repeat5:", round(repeat5, 4), "s")
    print("repeat10:", round(repeat10, 4), "s")
    caput(pv.me14e_gp104, round(repeat1, 4))
    caput(pv.me14e_gp105, round(repeat2, 4))
    caput(pv.me14e_gp106, round(repeat3, 4))
    caput(pv.me14e_gp107, round(repeat5, 4))
    caput(pv.me14e_gp108, round(repeat10, 4))
    print(8 * "Done ")


def block_check():
    name = inspect.stack()[0][3]
    caput(pv.me14e_gp9, 0)
    while True:
        if int(caget(pv.me14e_gp9)) == 0:
            chip_type = int(caget(pv.me14e_gp1))
            if chip_type == 9:
                block_start_list = scrape_pvar_file("minichip_oxford.pvar")
            if chip_type == 10:
                block_start_list = scrape_pvar_file("oxford6x6.pvar")
            else:
                block_start_list = scrape_pvar_file("sacla3_oxford.pvar")
            for entry in block_start_list:
                if int(caget(pv.me14e_gp9)) != 0:
                    logger.warning("%s Block Check Aborted" % (name))
                    print(50 * "Aborted")
                    sleep(1.0)
                    break
                block, x, y = entry
                print(block, x, y)
                logger.info("%s %s %s %s" % (name, block, x, y))
                caput(pv.me14e_pmac_str, "!x%sy%s" % (x, y))
                time.sleep(0.4)
        else:
            print("Block Check Aborted due to GP 9 not equalling 0")
            logger.warning(
                "%s Block Check Aborted due to GP 9 not equalling 0" % (name)
            )
            break
        break
    print(10 * "Done ")


def main(args):
    setup_logging()
    name = inspect.stack()[0][3]
    print(args)
    logger.info("%s \n\n%s" % (name, args))
    if args[1] == "initialise":
        initialise()
    elif args[1] == "pvar_test":
        chipid = args[2]
        # pvar_test(chipid) # TODO find out what this is supposed to be!!!
    elif args[1] == "moveto":
        moveto(args[2])
    elif args[1] == "fiducial":
        fiducial(args[2])
    elif args[1] == "cs_maker":
        cs_maker()
    elif args[1] == "pumpprobe_calc":
        pumpprobe_calc()
    elif args[1] == "write_parameter_file":
        write_parameter_file()
        startup.run()
    elif args[1] == "define_current_chip":
        chipid = args[2]
        define_current_chip(chipid)
    elif args[1] == "load_stock_map":
        map_choice = args[2]
        load_stock_map(map_choice)
    elif args[1] == "load_lite_map":
        load_lite_map()
    elif args[1] == "load_full_map":
        load_full_map()
    elif args[1] == "save_screen_map":
        save_screen_map()
    elif args[1] == "upload_full":
        upload_full()
    elif args[1] == "upload_parameters":
        chipid = args[2]
        upload_parameters(chipid)
    elif args[1] == "cs_reset":
        cs_reset()
    elif args[1] == "block_check":
        block_check()

    else:
        print("Unknown Command")
        logger.warning("Unknown Command" % name)


if __name__ == "__main__":
    main(sys.argv)
