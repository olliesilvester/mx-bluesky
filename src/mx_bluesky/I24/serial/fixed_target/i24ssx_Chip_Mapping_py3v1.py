"""
Chip mapping utilities for fixed target

This version changed to python3 March2020 by RLO
"""
import inspect
import logging
import string
import time

import numpy as np
from matplotlib import pyplot as plt

from mx_bluesky.I24.serial import log
from mx_bluesky.I24.serial.fixed_target.i24ssx_Chip_StartUp_py3v1 import (
    check_files,
    get_format,
    get_shot_order,
    get_xy,
    pathli,
    scrape_parameter_file,
    write_file,
)

logger = logging.getLogger("I24ssx.chip_mapping")


def setup_logging():
    # Log should now change name daily.
    logfile = time.strftime("i24_%Y_%m_%d.log").lower()
    log.config(logfile)


def read_file_make_dict(fid, chip_type, switch=False):
    name = inspect.stack()[0][3]
    logger.info("%s" % name)
    f = open(fid, "r")
    a_dict = {}
    b_dict = {}
    for line in f.readlines():
        if line.startswith("#"):
            continue
        else:
            entry = line.rstrip().split()
            addr = entry[0][-5:]
            pres = entry[4]
            x, y = get_xy(addr, chip_type)
            a_dict[x, y] = pres
            b_dict[addr] = pres
    if switch is True:
        return b_dict
    else:
        return a_dict


def plot_file(fid, chip_type):
    name = inspect.stack()[0][3]
    logger.info("%s" % name)
    chip_dict = read_file_make_dict(fid, chip_type)
    x_list, y_list, z_list = [], [], []
    for k in sorted(chip_dict.keys()):
        x, y = k[0], k[1]
        pres = chip_dict[k]
        x_list.append(float(x))
        y_list.append(float(y))
        z_list.append(float(pres))

    X = np.array(x_list)
    Y = np.array(y_list)
    Z = np.array(z_list)
    xr = X.ravel()
    yr = Y.ravel()
    zr = Z.ravel()

    fig = plt.figure(num=None, figsize=(12, 12), facecolor="0.6", edgecolor="k")
    fig.subplots_adjust(
        left=0.03, bottom=0.03, right=0.97, top=0.97, wspace=0, hspace=0
    )
    ax1 = fig.add_subplot(111, aspect="equal", axisbg="0.3")
    ax1.scatter(xr, yr, c=zr, s=8, alpha=1, marker="s", linewidth=0.1, cmap="winter")
    ax1.set_xlim(-1, 26)
    ax1.set_ylim(-1, 26)
    ax1.invert_yaxis()
    check_files(["%s.png" % chip_type])
    plt.savefig("%s.png" % fid[:-5], dpi=200, bbox_inches="tight", pad_inches=0.05)
    return 1


def get_hamburg_order():
    name = inspect.stack()[0][3]
    logger.info("%s" % (name))
    blk_num = 3
    caps = [
        "A",
        "B",
        "C",
        "C",
        "B",
        "A",
        "A",
        "B",
        "C",
        "C",
        "B",
        "A",
        "A",
        "B",
        "C",
        "C",
        "B",
        "A",
    ]
    nums = [
        "1",
        "1",
        "1",
        "1",
        "1",
        "1",
        "2",
        "2",
        "2",
        "2",
        "2",
        "2",
        "3",
        "3",
        "3",
        "3",
        "3",
        "3",
    ]
    lowercase_list = list(string.ascii_lowercase + string.ascii_uppercase + "0")

    block_list = []
    for a, b in zip(caps, nums):
        block_list.append(a + b)

    A_path = pathli(lowercase_list, "expand28", 0)
    B_path = pathli(lowercase_list[:28], "snake53", 0)
    window_dn = []
    for a, b in zip(A_path, B_path):
        window_dn.append(a + b)

    A_path = pathli(lowercase_list, "expand25", 1)
    B_path = pathli(lowercase_list[28:], "snake53", 0)
    window_up = []
    for a, b in zip(A_path, B_path):
        window_up.append(a + b)

    switch = 0
    count = 0
    collect_list = []
    for block in block_list:
        if switch == 0:
            for window in window_dn:
                collect_list.append(block + "_" + window)
            count += 1
            if count == blk_num:
                count = 0
                switch = 1
        else:
            for window in window_up:
                collect_list.append(block + "_" + window)
            count += 1
            if count == blk_num:
                count = 0
                switch = 0

    print(len(collect_list))
    logger.info("%s length of collect_list = %s" % (name, len(collect_list)))
    g = open("collect_list.txt", "w")
    for x in collect_list:
        g.write("%s\n" % x)
    g.close()

    return collect_list


def convert_chip_to_hex(fid, chip_type):
    name = inspect.stack()[0][3]
    logger.info("%s" % name)
    chip_dict = read_file_make_dict(fid, chip_type, True)
    chip_format = get_format(chip_type)
    check_files(["%s.full" % chip_type])
    g = open("%s.full" % fid[:-5], "w")
    # Normal
    if chip_type in ["0", "1", "5"]:
        shot_order_list = get_shot_order(chip_type)
        logger.info("%s Shot Order List: \n" % (name))
        logger.info("%s" % shot_order_list[:14])
        logger.info("%s" % shot_order_list[-14:])
        print(shot_order_list[:14])
        print(shot_order_list[-14:])
        for i, k in enumerate(shot_order_list):
            if i % 20 == 0:
                print()
                logger.info("\n")
            else:
                print(k, end=" ")
                logger.info("%s" % k)
        sorted_pres_list = []
        for addr in shot_order_list:
            sorted_pres_list.append(chip_dict[addr])

        windows_per_block = chip_format[2]
        number_of_lines = len(sorted_pres_list) / windows_per_block
        hex_length = windows_per_block / 4
        pad = 7 - hex_length
        for i in range(number_of_lines):
            sublist = sorted_pres_list[
                i * windows_per_block : (i * windows_per_block) + windows_per_block
            ]
            if i % 2 == 0:
                right_list = sublist
            else:
                right_list = sublist[::-1]
            hex_string = ("{0:0>%sX}" % hex_length).format(
                int("".join(str(x) for x in right_list), 2)
            )
            hex_string = hex_string + pad * "0"
            pvar = 5001 + i
            line = "P%s=$%s" % (pvar, hex_string)
            g.write(line + "\n")
            print(
                ("{0:0>%sX}" % hex_length).format(
                    int("".join(str(x) for x in right_list), 2)
                )
                + 4 * "0",
                end=" ",
            )
            print(i, right_list, end=" ")
            print("".join(str(x) for x in right_list), end=" ")
            print(line)
            logger.info(
                "%s %s \n"
                % (
                    name,
                    ("{0:0>%sX}" % hex_length).format(
                        int("".join(str(x) for x in right_list), 2)
                    )
                    + 4 * "0",
                )
            )
            logger.info("%s %s %s \n" % (name, i, right_list))
            logger.info("%s %s\n" % (name, "".join(str(x) for x in right_list)))
            logger.info("%s %s \n" % (name, line))
            if (i + 1) % windows_per_block == 0:
                print("\n", 40 * (" %i" % ((i / windows_per_block) + 2)))
                logger.info("\n %s" % (40 * (" %i" % ((i / windows_per_block) + 2))))
        print(hex_length)
        logger.info("%s hex_length: %s" % (name, hex_length))
    # NICHT Normal
    else:
        logger.info("%s Dealing with Hamburg \n" % (name))
        print("Dealing with Hamburg")
        shot_order_list = get_hamburg_order()
        print(shot_order_list[:14])
        print(shot_order_list[-14:])
        logger.info("%s Shot Order List: \n" % (name))
        logger.info("%s" % shot_order_list[:14])
        logger.info("%s" % shot_order_list[-14:])
        sorted_pres_list = []
        for addr in shot_order_list:
            sorted_pres_list.append(chip_dict[addr])
        even_odd = 0
        i = 0
        for col in range(6):
            if col % 2 == 0:
                for line in range(159):
                    chomp = []
                    for x in range(28):
                        chomp.append(sorted_pres_list.pop(0))
                    if even_odd % 2 == 0:
                        bite = chomp
                    else:
                        bite = chomp[::-1]
                    even_odd += 1
                    if even_odd == 53:
                        even_odd = 0
                    hex_string = ("{0:0>7X}").format(
                        int("".join(str(x) for x in bite), 2)
                    )
                    pvar = 5001 + i
                    writeline = "P%s=$%s" % (pvar, hex_string)
                    g.write(writeline + "\n")
                    print(line, "".join(str(x) for x in bite), end=" ")
                    print(("{0:0>7X}").format(int("".join(str(x) for x in bite), 2)))
                    logger.info("%s %s \n" % (line, "".join(str(x) for x in bite)))
                    logger.info(
                        "%s \n"
                        % (("{0:0>7X}").format(int("".join(str(x) for x in bite), 2)))
                    )
                    i += 1
                print()
            else:
                for line in range(159):
                    chomp = []
                    for x in range(25):
                        chomp.append(sorted_pres_list.pop(0))
                    if even_odd % 2 == 0:
                        bite = chomp
                    else:
                        bite = chomp[::-1]
                    bite += ["0", "0", "0"]
                    even_odd += 1
                    if even_odd == 53:
                        even_odd = 0
                    hex_string = ("{0:0>7X}").format(
                        int("".join(str(x) for x in bite), 2)
                    )
                    pvar = 5001 + i
                    writeline = "P%s=$%s" % (pvar, hex_string)
                    g.write(writeline + "\n")
                    print(line, "".join(str(x) for x in bite), end=" ")
                    print(("{0:0>7X}").format(int("".join(str(x) for x in bite), 2)))
                    logger.info("%s %s \n" % (line, "".join(str(x) for x in bite)))
                    logger.info(
                        "%s \n"
                        % (("{0:0>7X}").format(int("".join(str(x) for x in bite), 2)))
                    )
                    i += 1
                print()
            print("----------------------------------")
    g.close()
    return 0


def main():
    setup_logging()
    name = inspect.stack()[0][3]
    logger.info("%s" % name)
    (
        chip_name,
        visit,
        sub_dir,
        n_exposures,
        chip_type,
        map_type,
    ) = scrape_parameter_file()

    check_files([".spec"])
    write_file(suffix=".spec", order="shot")

    param_path = "/dls_sw/i24/scripts/fastchips/parameter_files/"
    logger.info("%s PARAMETER PATH = %s" % (name, param_path))
    print("param_path", param_path)
    fid = param_path + chip_name + ".spec"
    logger.info("%s FID = %s" % (name, fid))
    print("FID", fid)

    plot_file(fid, chip_type)
    convert_chip_to_hex(fid, chip_type)


if __name__ == "__main__":
    main()
    plt.show()
plt.close()
