"""
Cleaner abstractions of the PV table.

Takes the PV tables from I24's setup_beamline and wraps a slightly more
abstract wrapper around them.
"""
from __future__ import annotations

from typing import Union

from mx_bluesky.I24.serial.parameters import SSXType
from mx_bluesky.I24.serial.setup_beamline import pv

# Detectors


class Pilatus:
    id = 58
    name = "pilatus"

    # fast, slow / width, height
    image_size_pixels = (2463, 2527)
    pixel_size_mm = (0.172, 0.172)
    image_size_mm = tuple(
        round(a * b, 3) for a, b in zip(image_size_pixels, pixel_size_mm)
    )

    det_y_threshold = 50.0
    det_y_target = 0.0

    class pv:
        detector_distance = pv.pilat_detdist
        wavelength = pv.pilat_wavelength
        transmission = pv.pilat_filtertrasm
        file_name = pv.pilat_filename
        file_path = pv.pilat_filepath
        file_template = pv.pilat_filetemplate
        file_number = pv.pilat_filenumber
        beamx = pv.pilat_beamx
        beamy = pv.pilat_beamy


class Eiger:
    id = 94
    name = "eiger"

    pixel_size_mm = (0.075, 0.075)
    image_size_pixels = (3108, 3262)

    image_size_mm = tuple(
        round(a * b, 3) for a, b in zip(image_size_pixels, pixel_size_mm)
    )

    det_y_threshold = 200.0
    det_y_target = 220.0

    class pv:
        detector_distance = pv.eiger_detdist
        wavelength = pv.eiger_wavelength
        transmission = "BL24I-EA-PILAT-01:cam1:FilterTransm"
        file_name = pv.eiger_ODfilename
        file_path = pv.eiger_ODfilepath
        file_template = None
        sequence_id = pv.eiger_seqID
        beamx = pv.eiger_beamx
        beamy = pv.eiger_beamy


# Experiment types


class Extruder:
    expt_type = SSXType.EXTRUDER

    class pv:
        visit = pv.ioc12_gp1
        directory = pv.ioc12_gp2
        filename = pv.ioc12_gp3
        exp_time = pv.ioc12_gp5
        det_dist = pv.ioc12_gp7
        det_type = pv.ioc12_gp15
        pump_exp = pv.ioc12_gp9
        pump_delay = pv.ioc12_gp10
        spec_pv = {
            "num_imgs": pv.ioc12_gp4,
            "pump_status": pv.ioc12_gp6,  # if 1, true
        }


class FixedTarget:
    expt_type = SSXType.FIXED

    class pv:
        visit = pv.me14e_gp100
        directory = pv.me14e_filepath
        filename = pv.me14e_chip_name
        exp_time = pv.me14e_exptime
        det_dist = pv.me14e_dcdetdist
        det_type = pv.me14e_gp101
        pump_exp = pv.me14e_gp103
        pump_delay = pv.me14e_gp110
        spec_pv = {
            "chip_type": pv.me14e_gp1,
            "map_type": pv.me14e_gp2,
            "n_exposures": pv.me14e_gp3,
            "pump_repeat": pv.me14e_gp4,
            "prepump_exp": pv.me14e_gp109,
        }


#
Detector = Union[Pilatus, Eiger]
ExperimentType = Union[Extruder, FixedTarget]
