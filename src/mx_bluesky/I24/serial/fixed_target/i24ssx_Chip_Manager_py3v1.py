"""
Chip manager for fixed target
This version changed to python3 March2020 by RLO
"""
from __future__ import annotations

import argparse
import inspect
import json
import logging
import shutil
import sys
import time
from pathlib import Path
from time import sleep

import numpy as np

from mx_bluesky.I24.serial import log
from mx_bluesky.I24.serial.fixed_target import i24ssx_Chip_Mapping_py3v1 as mapping
from mx_bluesky.I24.serial.fixed_target import i24ssx_Chip_StartUp_py3v1 as startup
from mx_bluesky.I24.serial.parameters.constants import (
    CS_FILES_PATH,
    FULLMAP_PATH,
    LITEMAP_PATH,
    PARAM_FILE_PATH_FT,
    PVAR_FILE_PATH,
)
from mx_bluesky.I24.serial.setup_beamline import caget, caput, pv
from mx_bluesky.I24.serial.setup_beamline import setup_beamline as sup

logger = logging.getLogger("I24ssx.chip_manager")


def _coerce_to_path(path: Path | str) -> Path:
    if not isinstance(path, Path):
        return Path(path)
    return path


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

    param_path = _coerce_to_path(param_path)

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
    startup.run()


def scrape_pvar_file(fid: str, pvar_dir: Path | str = PVAR_FILE_PATH):
    block_start_list = []
    pvar_dir = _coerce_to_path(pvar_dir)

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
    if chipid == "oxford":
        caput(pv.me14e_gp1, 1)

    param_path = _coerce_to_path(param_path)

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
    litemap_path = _coerce_to_path(litemap_path)

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
    if chipid == "oxford":
        caput(pv.me14e_gp1, 1)
        width = 8
    litemap_path = _coerce_to_path(litemap_path)

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
    fullmap_path = _coerce_to_path(fullmap_path)

    with open(fullmap_path / "currentchip.full", "r") as fh:
        f = fh.readlines()

    for i in range(len(f) // 2):
        pmac_list = []
        for j in range(2):
            pmac_list.append(f.pop(0).rstrip("\n"))
        writeline = " ".join(pmac_list)
        print(writeline)
        logger.info("%s %s" % (name, writeline))
        caput(pv.me14e_pmac_str, writeline)
        sleep(0.02)

    print(10 * "Done ")
    logger.info("%s %s" % (name, 10 * "Done"))


def load_stock_map(map_choice: str):
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
    chip_type = int(caget(pv.me14e_gp1))
    if chip_type in [0, 1]:
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

    litemap_path = _coerce_to_path(litemap_path)

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


def load_full_map(fullmap_path: Path | str = FULLMAP_PATH):
    name = inspect.stack()[0][3]
    (
        chip_name,
        visit,
        sub_dir,
        n_exposures,
        chip_type,
        map_type,
    ) = startup.scrape_parameter_file()
    fullmap_path = _coerce_to_path(fullmap_path)

    fullmap_fid = fullmap_path / f"{str(caget(pv.me14e_gp5))}.spec"
    print("opening", fullmap_fid)
    logger.info("%s opening %s" % (name, fullmap_fid))
    mapping.plot_file(fullmap_fid, chip_type)
    print("\n\n", 10 * "PNG ")
    mapping.convert_chip_to_hex(fullmap_fid, chip_type)
    shutil.copy2(fullmap_fid.with_suffix(".full"), fullmap_path / "currentchip.full")
    logger.info(
        "%s copying %s to %s"
        % (name, fullmap_fid.with_suffix(".full"), fullmap_path / "currentchip.full")
    )
    print(10 * "Done ", "\n")


def moveto(place: str):
    name = inspect.stack()[0][3]
    logger.info("%s Move to %s" % (name, place))
    print(5 * (place + " "))
    chip_type = int(caget(pv.me14e_gp1))
    print("CHIP TYPE", chip_type)

    if chip_type == 0 or chip_type == 3:
        # Oxford and minichip
        # As minichip is nothing more than a smaller oxford, they should move the same way
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

    elif chip_type == 1:
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

    elif chip_type == 2:
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

    else:
        logger.warning("%s Unknown chip_type move" % name)

    # Non Chip Specific Move
    if place == "zero":
        logger.info("%s moving to %s" % (name, place))
        caput(pv.me14e_pmac_str, "!x0y0z0")

    elif place == "load_position":
        print("load position")
        logger.info("%s %s" % (name, place))
        caput(pv.bs_mp_select, "Robot")
        caput(pv.bl_mp_select, "Out")
        caput(pv.det_z, 1300)

    elif place == "collect_position":
        print("collect position")
        logger.info("%s %s" % (name, place))
        caput(pv.me14e_filter, 20)
        caput(pv.me14e_stage_x, 0.0)
        caput(pv.me14e_stage_y, 0.0)
        caput(pv.me14e_stage_z, 0.0)
        caput(pv.bs_mp_select, "Data Collection")
        caput(pv.bl_mp_select, "In")

    elif place == "microdrop_position":
        print("microdrop align position")
        logger.info("%s %s" % (name, place))
        caput(pv.me14e_stage_x, 6.0)
        caput(pv.me14e_stage_y, -7.8)
        caput(pv.me14e_stage_z, 0.0)

    elif place == "laser1on":  # these are in laser edm
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


def scrape_mtr_directions(param_path: Path | str = CS_FILES_PATH):
    name = inspect.stack()[0][3]
    param_path = _coerce_to_path(param_path)

    with open(param_path / "motor_direction.txt", "r") as f:
        lines = f.readlines()
    mtr1_dir, mtr2_dir, mtr3_dir = 1.0, 1.0, 1.0
    for line in lines:
        if line.startswith("mtr1"):
            mtr1_dir = float(line.split("=")[1])
        elif line.startswith("mtr2"):
            mtr2_dir = float(line.split("=")[1])
        elif line.startswith("mtr3"):
            mtr3_dir = float(line.split("=")[1])
        else:
            continue
    logger.info(
        "%s mt1_dir %s mtr2_dir %s mtr3_dir %s" % (name, mtr1_dir, mtr2_dir, mtr3_dir)
    )
    return mtr1_dir, mtr2_dir, mtr3_dir


def fiducial(point: int, param_path: Path | str = PARAM_FILE_PATH_FT):
    name = inspect.stack()[0][3]
    scale = 10000.0  # noqa: F841
    param_path = _coerce_to_path(param_path)

    mtr1_dir, mtr2_dir, mtr3_dir = scrape_mtr_directions(param_path)

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

    with open(param_path / f"fiducial_{point}.txt", "w") as f:
        f.write("MTR\tRBV\tRAW\tCorr\tf_value\n")
        f.write("MTR1\t%1.4f\t%i\t%i\t%1.4f\n" % (rbv_1, raw_1, mtr1_dir, f_x))
        f.write("MTR2\t%1.4f\t%i\t%i\t%1.4f\n" % (rbv_2, raw_2, mtr2_dir, f_y))
        f.write("MTR3\t%1.4f\t%i\t%i\t%1.4f" % (rbv_3, raw_3, mtr3_dir, f_z))
    print(10 * "Done ")


def scrape_mtr_fiducials(point: int, param_path: Path | str = PARAM_FILE_PATH_FT):
    param_path = _coerce_to_path(param_path)

    with open(param_path / f"fiducial_{point}.txt", "r") as f:
        f_lines = f.readlines()[1:]
    f_x = float(f_lines[0].rsplit()[4])
    f_y = float(f_lines[1].rsplit()[4])
    f_z = float(f_lines[2].rsplit()[4])
    return f_x, f_y, f_z


def cs_maker():
    """
    Coordinate system.

    Values for scalex, scaley, scalez, and skew, as well as the sign of
    Sx, Sy, Sz are stored in a .json file and should be modified there.
    Location of file: src/mx_bluesky/I24/serial/parameters/cs_maker.json

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
    |1  0   0| | Cy 0 -Sy| |Cz  Sz 0|   | CyCz         CxSz         -Sy |
    |0 Cx  Sx|*|  0  1  0|*|-Sz Cz 0| = | SxSyCz-CxSz  SxSySz+CxCz  SxCy|
    |0 -Sx Cx| | Sy  0 Cy| | 0   0 1|   | CxSyCz+SxSz  CxSySz-SxCz  CxCy|


    Skew:
    Skew is the difference between the Sz1 and Sz2 after rotation is taken out.
    This should be measured in situ prior to expriment, ie. measure by hand using
    opposite and adjacent RBV after calibration of scale factors.
    """
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

    # Scale parameters saved in json file
    with open(CS_FILES_PATH / "cs_maker.json", "r") as fh:
        cs_info = json.load(fh)

    scalex, scaley, scalez = cs_info["scalex"], cs_info["scaley"], cs_info["scalez"]
    skew = cs_info["skew"]

    # Rotation Around Z
    # If stages upsidedown (I24) change sign of Sz
    Sz1 = -1 * f1_y / fiducial_dict[chip_type][0]
    Sz2 = f2_x / fiducial_dict[chip_type][1]
    Sz = cs_info["Sz_dir"] * ((Sz1 + Sz2) / 2)
    Cz = np.sqrt((1 - Sz**2))
    print("Sz1 , %1.4f, %1.4f" % (Sz1, np.degrees(np.arcsin(Sz1))))
    logger.info("%s Sz1 , %1.4f, %1.4f" % (name, Sz1, np.degrees(np.arcsin(Sz1))))
    print("Sz2 , %1.4f, %1.4f" % (Sz2, np.degrees(np.arcsin(Sz2))))
    logger.info("%s Sz2 , %1.4f, %1.4f" % (name, Sz2, np.degrees(np.arcsin(Sz2))))
    print("Sz ,  %1.4f, %1.4f" % (Sz, np.degrees(np.arcsin(Sz))))
    logger.info("%s Sz , %1.4f, %1.4f" % (name, Sz, np.degrees(np.arcsin(Sz))))
    print("Cz ,  %1.4f, %1.4f\n" % (Cz, np.degrees(np.arccos(Cz))))
    logger.info("%s Cz , %1.4f, %1.4f" % (name, Cz, np.degrees(np.arcsin(Cz))))
    # Rotation Around Y
    Sy = cs_info["Sy_dir"] * f1_z / fiducial_dict[chip_type][0]
    Cy = np.sqrt((1 - Sy**2))
    print("Sy , %1.4f, %1.4f" % (Sy, np.degrees(np.arcsin(Sy))))
    logger.info("%s Sy , %1.4f, %1.4f" % (name, Sy, np.degrees(np.arcsin(Sy))))
    print("Cy , %1.4f, %1.4f\n" % (Cy, np.degrees(np.arccos(Cy))))
    logger.info("%s Cy , %1.4f, %1.4f" % (name, Cy, np.degrees(np.arcsin(Cy))))
    # Rotation Around X
    # If stages upsidedown (I24) change sign of Sx
    Sx = cs_info["Sx_dir"] * f2_z / fiducial_dict[chip_type][1]
    Cx = np.sqrt((1 - Sx**2))
    print("Sx , %1.4f, %1.4f" % (Sx, np.degrees(np.arcsin(Sx))))
    logger.info("%s Sx , %1.4f, %1.4f" % (name, Sx, np.degrees(np.arcsin(Sx))))
    print("Cx , %1.4f, %1.4f\n" % (Cx, np.degrees(np.arccos(Cx))))
    logger.info("%s Cx , %1.4f, %1.4f" % (name, Cx, np.degrees(np.arcsin(Cx))))

    x1factor = mtr1_dir * scalex * (Cy * Cz)
    y1factor = mtr2_dir * scaley * (-1.0 * Cx * Sz)
    z1factor = mtr3_dir * scalez * Sy

    x2factor = mtr1_dir * scalex * ((Sx * Sy * Cz) + (Cx * Sz))
    y2factor = mtr2_dir * scaley * ((Cx * Cz) - (Sx * Sy * Sz))
    z2factor = mtr3_dir * scalez * (-1.0 * Sx * Cy)

    x3factor = mtr1_dir * scalex * ((Sx * Sz) - (Cx * Sy * Cz))
    y3factor = mtr2_dir * scaley * ((Cx * Sy * Sz) + (Sx * Cz))
    z3factor = mtr3_dir * scalez * (Cx * Cy)

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
    if str(chip_type) == "0":
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
            if chip_type == 3:
                logger.info("Oxford mini chip in use.")
                block_start_list = scrape_pvar_file("minichip_oxford.pvar")
            elif chip_type == 2:
                logger.error("This is a custom chip, no block check available!")
                raise ValueError(
                    "Chip type set to 'custom', which has no block check."
                    "If not using a custom chip, please double check chip in the GUI."
                )
            else:
                logger.warning("Default is Oxford chip block start list.")
                block_start_list = scrape_pvar_file("oxford.pvar")
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


if __name__ == "__main__":
    setup_logging()

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        help="Choose command.",
        required=True,
        dest="sub-command",
    )
    parser_init = subparsers.add_parser(
        "initialise",
    )
    parser_init.set_defaults(func=initialise)
    parser_moveto = subparsers.add_parser(
        "moveto",
    )
    parser_moveto.add_argument("place", type=str)
    parser_moveto.set_defaults(func=moveto)
    parser_fid = subparsers.add_parser("fiducial")
    parser_fid.add_argument("point", type=int)
    parser_fid.set_defaults(func=fiducial)
    parser_csm = subparsers.add_parser("cs_maker")
    parser_csm.set_defaults(func=cs_maker)
    parser_pp = subparsers.add_parser("pumpprobe_calc")
    parser_pp.set_defaults(func=pumpprobe_calc)
    parser_write = subparsers.add_parser("write_parameter_file")
    parser_write.set_defaults(func=write_parameter_file)
    parser_def = subparsers.add_parser("define_current_chip")
    parser_def.add_argument("chipid", type=str)
    parser_def.set_defaults(func=define_current_chip)
    parser_stockmap = subparsers.add_parser("load_stock_map")
    parser_stockmap.add_argument("map_choice", type=str)
    parser_stockmap.set_defaults(func=load_stock_map)
    parser_litemap = subparsers.add_parser("load_lite_map")
    parser_litemap.set_defaults(func=load_lite_map)
    parser_fullmap = subparsers.add_parser("load_full_map")
    parser_fullmap.set_defaults(func=load_full_map)
    parser_save = subparsers.add_parser("save_screen_map")
    parser_save.set_defaults(func=save_screen_map)
    parser_upld = subparsers.add_parser("upload_full")
    parser_upld.set_defaults(func=upload_full)
    parser_params = subparsers.add_parser("upload_parameters")
    parser_params.add_argument("chipid", type=str)
    parser_params.set_defaults(func=upload_parameters)
    parser_csr = subparsers.add_parser("cs_reset")
    parser_csr.set_defaults(func=cs_reset)
    parser_block = subparsers.add_parser("block_check")
    parser_block.set_defaults(func=block_check)

    args = parser.parse_args()
    args.func(args)
