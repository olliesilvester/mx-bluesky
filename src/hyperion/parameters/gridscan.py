from __future__ import annotations

import numpy as np
from dodal.devices.detector import DetectorParams
from dodal.devices.fast_grid_scan import GridScanParams
from dodal.devices.panda_fast_grid_scan import PandAGridScanParams
from pydantic import Field, validator
from scanspec.core import Path as ScanPath
from scanspec.specs import Line

from hyperion.external_interaction.ispyb.ispyb_dataclass import (
    GridscanIspybParams,
)
from hyperion.parameters.components import (
    DiffractionExperiment,
    OptionalGonioAngleStarts,
    SplitScan,
    TemporaryIspybExtras,
    WithSample,
    WithScan,
    XyzAxis,
    XyzStarts,
)
from hyperion.parameters.constants import CONST
from hyperion.parameters.plan_specific.gridscan_internal_params import (
    GridscanHyperionParameters,
    GridscanInternalParameters,
    OddYStepsException,
)
from hyperion.parameters.plan_specific.panda.panda_gridscan_internal_params import (
    PandAGridscanInternalParameters,
)


class GridCommon(DiffractionExperiment, OptionalGonioAngleStarts, WithSample):
    grid_width_um = CONST.PARAM.GRIDSCAN.WIDTH_UM
    exposure_time_s: float = CONST.PARAM.GRIDSCAN.EXPOSURE_TIME_S
    use_roi_mode: bool = CONST.PARAM.GRIDSCAN.USE_ROI
    transmission_frac: float = 1
    # field rather than inherited to make it easier to track when it can be removed:
    ispyb_extras: TemporaryIspybExtras


class GridScanWithEdgeDetect(GridCommon, WithSample): ...


class PinTipCentreThenXrayCentre(GridCommon):
    tip_offset_um: float = 0


class RobotLoadThenCentre(GridCommon, WithSample): ...


class SpecifiedGridScan(GridCommon, XyzStarts, WithScan, WithSample):
    panda_runup_distance_mm: float = Field(default=CONST.I03.PANDA_RUNUP_DIST_MM)

    @property
    def detector_params(self):
        detector_params = {
            "expected_energy_ev": self.demand_energy_ev,
            "exposure_time": self.exposure_time_s,
            "directory": str(
                self.visit_directory / "xraycentring" / str(self.sample_id)
            ),
            "prefix": self.file_name,
            "detector_distance": self.detector_distance_mm,
            "omega_start": self.omega_start_deg,
            "omega_increment": 0,
            "num_images_per_trigger": 1,
            "num_triggers": self.num_images,
            "use_roi_mode": self.use_roi_mode,
            "det_dist_to_beam_converter_path": self.det_dist_to_beam_converter_path,
            "run_number": self.run_number,
            "trigger_mode": self.trigger_mode,
        }
        return DetectorParams(**detector_params)

    @property
    def ispyb_params(
        self,
    ):
        return GridscanIspybParams(
            visit_path=str(self.visit_directory),
            microns_per_pixel_x=self.ispyb_extras.microns_per_pixel_x,
            microns_per_pixel_y=self.ispyb_extras.microns_per_pixel_y,
            position=np.array(self.ispyb_extras.position),
            transmission_fraction=self.transmission_frac,
            current_energy_ev=self.demand_energy_ev,
            beam_size_x=self.ispyb_extras.beam_size_x,
            beam_size_y=self.ispyb_extras.beam_size_y,
            focal_spot_size_x=self.ispyb_extras.focal_spot_size_x,
            focal_spot_size_y=self.ispyb_extras.focal_spot_size_y,
            comment=self.comment,
            resolution=self.ispyb_extras.resolution,
            sample_id=str(self.sample_id),
            sample_barcode=self.ispyb_extras.sample_barcode,
            flux=self.ispyb_extras.flux,
            undulator_gap=self.ispyb_extras.undulator_gap,
            synchrotron_mode=self.ispyb_extras.synchrotron_mode,
            slit_gap_size_x=self.ispyb_extras.slit_gap_size_x,
            slit_gap_size_y=self.ispyb_extras.slit_gap_size_x,
            xtal_snapshots_omega_start=self.ispyb_extras.xtal_snapshots_omega_start
            or [],
            xtal_snapshots_omega_end=self.ispyb_extras.xtal_snapshots_omega_end or [],
            ispyb_experiment_type=self.ispyb_extras.ispyb_experiment_type,
            upper_left=np.array(self.ispyb_extras.upper_left),
        )


class TwoDGridScan(SpecifiedGridScan):
    demand_energy_ev: float | None = Field(default=None)
    omega_start_deg: float | None = Field(default=None)
    axis_1_step_size_um: float = Field(default=CONST.PARAM.GRIDSCAN.APERTURE_SIZE)
    axis_2_step_size_um: float = Field(default=CONST.PARAM.GRIDSCAN.APERTURE_SIZE)
    axis_1: XyzAxis = XyzAxis.X
    axis_2: XyzAxis = XyzAxis.Y
    axis_1_steps: int
    axis_2_steps: int

    @validator("axis_2")
    def _validate_axis_2(cls, axis_2: XyzAxis, values) -> XyzAxis:
        if axis_2 == values["axis_1"]:
            raise ValueError(
                f"Axis 1 ({values['axis_1']}) and axis 2 ({axis_2}) cannot be equal!"
            )
        return axis_2

    @property
    def normal_axis(self) -> XyzAxis:
        """The axis not used in the gridscan, e.g. Z for a scan in Y and X"""
        return ({XyzAxis.X, XyzAxis.Y, XyzAxis.Z} ^ {self.axis_1, self.axis_2}).pop()

    @property
    def axis_1_start_um(self) -> float:
        return self.axis_1.for_axis(self.x_start_um, self.y_start_um, self.z_start_um)

    @property
    def axis_2_start_um(self) -> float:
        return self.axis_2.for_axis(self.x_start_um, self.y_start_um, self.z_start_um)

    @property
    def normal_axis_start(self) -> float:
        return self.normal_axis.for_axis(
            self.x_start_um, self.y_start_um, self.z_start_um
        )

    @property
    def axis_1_end_um(self) -> float:
        return self.axis_1_start_um + self.axis_1_step_size_um * self.axis_1_steps

    @property
    def axis_2_end_um(self) -> float:
        return self.axis_2_start_um + self.axis_2_step_size_um * self.axis_2_steps

    @property
    def num_images(self) -> int:
        return self.axis_1_steps * self.axis_2_steps

    @property
    def scan_spec(self):
        line_1 = Line(
            str(self.axis_1.value),
            self.axis_1_start_um,
            self.axis_1_end_um,
            self.axis_1_steps,
        )
        line_2 = Line(
            str(self.axis_2.value),
            self.axis_2_start_um,
            self.axis_2_end_um,
            self.axis_2_steps,
        )
        return line_2 * ~line_1

    @property
    def scan_points(self):
        return ScanPath(self.scan_spec.calculate()).consume().midpoints


class ThreeDGridScan(SpecifiedGridScan, SplitScan):
    demand_energy_ev: float | None = Field(default=None)
    omega_start_deg: float = Field(default=CONST.PARAM.GRIDSCAN.OMEGA_1)  # type: ignore
    omega2_start_deg: float = Field(default=CONST.PARAM.GRIDSCAN.OMEGA_2)
    x_step_size_um: float = Field(default=CONST.PARAM.GRIDSCAN.APERTURE_SIZE)
    y_step_size_um: float = Field(default=CONST.PARAM.GRIDSCAN.APERTURE_SIZE)
    z_step_size_um: float = Field(default=CONST.PARAM.GRIDSCAN.APERTURE_SIZE)
    y2_start_um: float
    z2_start_um: float
    x_steps: int
    y_steps: int
    z_steps: int

    @property
    def FGS_params(self) -> GridScanParams:
        return GridScanParams(
            x_steps=self.x_steps,
            y_steps=self.y_steps,
            z_steps=self.z_steps,
            x_step_size=self.x_step_size_um,
            y_step_size=self.y_step_size_um,
            z_step_size=self.z_step_size_um,
            x_start=self.x_start_um,
            y1_start=self.y_start_um,
            z1_start=self.z_start_um,
            y2_start=self.y2_start_um,
            z2_start=self.z2_start_um,
            set_stub_offsets=False,
            dwell_time_ms=self.exposure_time_s * 1000,
        )

    @property
    def panda_FGS_params(self) -> PandAGridScanParams:
        return PandAGridScanParams(
            x_steps=self.x_steps,
            y_steps=self.y_steps,
            z_steps=self.z_steps,
            x_step_size=self.x_step_size_um,
            y_step_size=self.y_step_size_um,
            z_step_size=self.z_step_size_um,
            x_start=self.x_start_um,
            y1_start=self.y_start_um,
            z1_start=self.z_start_um,
            y2_start=self.y2_start_um,
            z2_start=self.z2_start_um,
            set_stub_offsets=False,
            run_up_distance_mm=self.panda_runup_distance_mm,
        )

    @property
    def scan_1(self):
        x_end = self.x_start_um + self.x_step_size_um * self.x_steps
        y1_end = self.y_start_um + self.y_step_size_um * self.y_steps

        scan_1_x = Line("sam_x", self.x_start_um, x_end, self.x_steps)
        scan_1_omega = Line(
            "omega", self.omega_start_deg, self.omega_start_deg, self.x_steps
        )
        scan_1_z = Line("sam_z", self.z_start_um, self.z_start_um, self.x_steps)
        scan_1_y = Line("sam_y", self.y_start_um, y1_end, self.y_steps)
        return scan_1_x.zip(scan_1_z).zip(scan_1_omega) * ~scan_1_y

    @property
    def scan_2(self):
        x_end = self.x_start_um + self.x_step_size_um * self.x_steps
        z2_end = self.z2_start_um + self.z_step_size_um * self.z_steps

        scan_2_x = Line("sam_x", self.x_start_um, x_end, self.x_steps)
        scan_2_omega = Line(
            "omega", self.omega2_start_deg, self.omega2_start_deg, self.x_steps
        )
        scan_2_y = Line("sam_y", self.y2_start_um, self.y2_start_um, self.x_steps)
        scan_2_z = Line("sam_z", self.z2_start_um, z2_end, self.z_steps)
        return scan_2_x.zip(scan_2_y).zip(scan_2_omega) * ~scan_2_z

    @property
    def scan_indices(self):
        """The first index of each gridscan"""
        return [0, len(ScanPath(self.scan_1.calculate()).consume().midpoints["sam_x"])]

    @property
    def scan_spec(self):
        return self.scan_1.concat(self.scan_2)

    @property
    def scan_points(self):
        return ScanPath(self.scan_spec.calculate()).consume().midpoints

    @property
    def num_images(self) -> int:
        return len(self.scan_points["sam_x"])

    def old_parameters(self):
        return GridscanInternalParameters(
            params_version=str(self.parameter_model_version),  # type: ignore
            hyperion_params=GridscanHyperionParameters(
                zocalo_environment=self.zocalo_environment,
                beamline=self.beamline,
                insertion_prefix=self.insertion_prefix,
                experiment_type="flyscan_xray_centre",
                detector_params=self.detector_params,
                ispyb_params=self.ispyb_params,
            ),
            experiment_params=self.FGS_params,
        )

    def panda_old_parameters(self):
        if self.y_steps % 2 and self.z_steps > 0:
            raise OddYStepsException(
                "The number of Y steps must be even for a PandA gridscan"
            )
        return PandAGridscanInternalParameters(
            params_version=str(self.parameter_model_version),  # type: ignore
            hyperion_params=GridscanHyperionParameters(
                zocalo_environment=self.zocalo_environment,
                beamline=self.beamline,
                insertion_prefix=self.insertion_prefix,
                experiment_type="flyscan_xray_centre",
                detector_params=self.detector_params,
                ispyb_params=self.ispyb_params,
            ),
            experiment_params=self.panda_FGS_params,
        )
