import os
import pathlib
import pprint
import time

import requests

from mx_bluesky.I24.serial.setup_beamline import caget, cagetstring, pv


def call_nexgen(
    chip_prog_dict,
    start_time,
    param_file_tuple,
    expt_type="fixed_target",
    total_numb_imgs=None,
):
    det_type = str(caget(pv.me14e_gp101))
    print(f"det_type: {det_type}")

    if expt_type == "fixed_target":
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
        ) = param_file_tuple
        if map_type == 0 or int(chip_type) == 2:
            currentchipmap = "fullchip"
        else:
            currentchipmap = "/dls_sw/i24/scripts/fastchips/litemaps/currentchip.map"
    elif expt_type == "extruder":
        # chip_prog_dict should be None for extruder (passed as input for now)
        (
            visit,
            sub_dir,
            filename,
            num_imgs,
            exptime,
            dcdetdist,
            det_type,
            pump_status,
            pumpexptime,
            pumpdelay,
        ) = param_file_tuple
        total_numb_imgs = num_imgs
        currentchipmap = None
        pump_repeat = "0" if pump_status == "false" else "1"

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

    # filepath = visit + sub_dir
    # filename = chip_name
    transmission = (float(caget(pv.pilat_filtertrasm)),)
    wavelength = float(caget(pv.dcm_lambda))

    if det_type == "eiger":
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
            "det_dist": dcdetdist,
            "exp_time": exptime,
            "expt_type": expt_type,
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
