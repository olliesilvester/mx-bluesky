import os
import sys

from importlib_metadata import metadata


sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from dataclasses import dataclass, field
from src.artemis.devices.eiger import DetectorParams, EigerDetector
from src.artemis.ispyb.ispyb_dataclass import IspybParams, Orientation
from src.artemis.devices.fast_grid_scan import (
    FastGridScan,
    GridScanParams,
    set_fast_grid_scan_params,
)
import bluesky.preprocessors as bpp
import bluesky.plan_stubs as bps
from bluesky import RunEngine
from bluesky.utils import ProgressBarManager

from src.artemis.devices.zebra import Zebra
from src.artemis.devices.det_dim_constants import (
    EIGER2_X_16M_SIZE,
    DetectorSizeConstants,
    constants_from_type,
)
import argparse
from src.artemis.devices.det_dist_to_beam_converter import (
    DetectorDistanceToBeamXYConverter,
)

from ophyd.log import config_ophyd_logging
from bluesky.log import config_bluesky_logging

from dataclasses_json import dataclass_json, config

config_bluesky_logging(file="/tmp/bluesky.log", level="DEBUG")
config_ophyd_logging(file="/tmp/ophyd.log", level="DEBUG")

# Clear odin errors and check initialised
# If in error clean up
# Setup beamline
# Store in ISPyB
# Start nxgen
# Start analysis run collection
SIM_BEAMLINE = "BL03S"


@dataclass_json
@dataclass
class FullParameters:
    detector_size_constants: DetectorSizeConstants = field(
        default=EIGER2_X_16M_SIZE,
        metadata=config(
            encoder=lambda detector: detector.det_type_string,
            decoder=lambda det_type: constants_from_type(det_type),
        ),
    )

    beam_xy_converter: DetectorDistanceToBeamXYConverter = field(
        default=DetectorDistanceToBeamXYConverter(os.path.join(
                    os.path.dirname(__file__),
                    "devices",
                    "det_dist_to_beam_XY_converter.txt",
                )),
        metadata=config(
            encoder=lambda converter: converter.lookup_file,
            decoder=lambda path_name: DetectorDistanceToBeamXYConverter(path_name)
        )
    )

    beamline: str = SIM_BEAMLINE
    grid_scan_params: GridScanParams = GridScanParams(
        x_steps=5,
        y_steps=10,
        x_step_size=0.1,
        y_step_size=0.1,
        dwell_time=0.2,
        x_start=0.0,
        y1_start=0.0,
        z1_start=0.0,
    )
    detector_params: DetectorParams = DetectorParams(
        detector_size_constants=detector_size_constants,
        beam_xy_converter=beam_xy_converter,
        current_energy=100,
        exposure_time=0.1,
        acquisition_id="test",
        directory="/tmp",
        prefix="file_name",
        detector_distance=100.0,
        omega_start=0.0,
        omega_increment=0.1,
        num_images=10,
        use_roi_mode = False,
    )
    ispyb_params: IspybParams = IspybParams(
        sample_id=None,
        visit_path=None,
        undulator_gap=None,
        pixels_per_micron_x=None,
        pixels_per_micron_y=None,
        upper_left=[None,None],
        bottom_right=[None,None],
        sample_barcode=None,
        position=None,
        synchrotron_mode=None,
        xtal_snapshots=None,
        run_number=None,
        transmission=None,
        flux=None,
        wavelength=None,
        beam_size_x=None,
        beam_size_y=None,
        slit_gap_size_x=None,
        slit_gap_size_y=None,
        focal_spot_size_x=None,
        focal_spot_size_y=None,
        comment=None,
        resolution=None,
    )


@bpp.run_decorator()
def run_gridscan(
    fgs: FastGridScan, zebra: Zebra, eiger: EigerDetector, parameters: FullParameters
):
    # TODO: Check topup gate
    yield from set_fast_grid_scan_params(fgs, parameters.grid_scan_params)

    eiger.detector_size_constants = parameters.detector
    eiger.use_roi_mode = parameters.use_roi
    eiger.detector_params = parameters.detector_params
    eiger.beam_xy_converter = parameters.det_to_distance

    @bpp.stage_decorator([zebra, eiger, fgs])
    def do_fgs():
        yield from bps.kickoff(fgs)
        yield from bps.complete(fgs, wait=True)

    yield from do_fgs()


def get_plan(parameters: FullParameters):
    """Create the plan to run the grid scan based on provided parameters.

    Args:
        parameters (FullParameters): The parameters to run the scan.

    Returns:
        Generator: The plan for the gridscan
    """
    fast_grid_scan = FastGridScan(
        name="fgs", prefix=f"{parameters.beamline}-MO-SGON-01:FGS:"
    )
    eiger = EigerDetector(name="eiger", prefix=f"{parameters.beamline}-EA-EIGER-01:")
    zebra = Zebra(name="zebra", prefix=f"{parameters.beamline}-EA-ZEBRA-01:")

    return run_gridscan(fast_grid_scan, zebra, eiger, parameters)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--beamline",
        help="The beamline prefix this is being run on",
        default=SIM_BEAMLINE,
    )
    args = parser.parse_args()

    RE = RunEngine({})
    RE.waiting_hook = ProgressBarManager()

    parameters = FullParameters(beamline=args.beamline)

    RE(get_plan(parameters))
