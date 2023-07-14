from __future__ import annotations

import os
import pathlib
import pprint
import time
from datetime import datetime
from typing import Dict

import requests

from mx_bluesky.I24.serial.parameters import ExperimentParameters, SSXType
from mx_bluesky.I24.serial.setup_beamline import caget, cagetstring, pv


def call_nexgen(
    chip_prog_dict: Dict[str, str | float],
    start_time: datetime,
    params: ExperimentParameters,
    ssx_type: SSXType = SSXType.FIXED,
    total_numb_imgs: int | None = None,
):
    det_type = str(caget(pv.me14e_gp101))
    print(f"det_type: {det_type}")

    if ssx_type == SSXType.FIXED:
        chip_type = params.expt.chip_type  # type: ignore[union-attr]
        map_type = params.expt.map_type  # type: ignore[union-attr]
        pump_repeat = params.pump_probe.pump_repeat

        if map_type == 0 or int(chip_type) == 2:
            currentchipmap = "fullchip"
        else:
            currentchipmap = "/dls_sw/i24/scripts/fastchips/litemaps/currentchip.map"

    elif ssx_type == SSXType.EXTRUDER:
        # chip_prog_dict should be None for extruder (passed as input for now)
        total_numb_imgs = params.expt.num_imgs  # type: ignore[union-attr]
        currentchipmap = None
        pump_repeat = "0" if params.pump_probe.pump_status == "false" else "1"

    visit = params.general.visit
    sub_dir = params.general.directory
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

    transmission = (float(caget(pv.pilat_filtertrasm)),)
    wavelength = float(caget(pv.dcm_lambda))

    if params.general.det_type == "eiger":
        print("nexgen here")
        print(chip_prog_dict)

        access_token = pathlib.Path("/scratch/ssx_nexgen.key").read_text().strip()
        url = "https://ssx-nexgen.diamond.ac.uk/ssx_eiger/write"
        headers = {"Authorization": f"Bearer {access_token}"}

        payload = {
            "beamline": "i24",
            "beam_center": [caget(pv.eiger_beamx), caget(pv.eiger_beamy)],
            "chipmap": currentchipmap,
            "chip_info": chip_prog_dict,
            "det_dist": params.general.det_dist,
            "exp_time": params.general.exp_time,
            "expt_type": params.expt.expt_type,
            "filename": filename_prefix,
            "num_imgs": total_numb_imgs,
            "pump_status": bool(float(pump_repeat)),
            "pump_exp": params.pump_probe.pump_exp,
            "pump_delay": params.pump_probe.pump_delay,
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
