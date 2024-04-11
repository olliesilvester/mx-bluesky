from __future__ import annotations

import datetime
from abc import abstractmethod
from enum import Enum
from pathlib import Path
from typing import Sequence, SupportsInt, TypeVar

import numpy as np
from dodal.devices.detector import (
    DetectorParams,
    TriggerMode,
)
from numpy.typing import NDArray
from pydantic import BaseModel, Extra, Field, validator
from scanspec.core import AxesPoints
from semver import Version

from hyperion.external_interaction.ispyb.ispyb_dataclass import (
    IspybParams,
)
from hyperion.parameters.constants import CONST

T = TypeVar("T")


class ParameterVersion(Version):
    @classmethod
    def _parse(cls, version):
        if isinstance(version, cls):
            return version
        return cls.parse(version)

    @classmethod
    def __get_validators__(cls):
        """Return a list of validator methods for pydantic models."""
        yield cls._parse

    @classmethod
    def __modify_schema__(cls, field_schema):
        """Inject/mutate the pydantic field schema in-place."""
        field_schema.update(examples=["1.0.2", "2.15.3-alpha", "21.3.15-beta+12345"])


PARAMETER_VERSION = ParameterVersion.parse("5.0.0")


class RotationAxis(str, Enum):
    OMEGA = "omega"
    PHI = "phi"
    CHI = "chi"
    KAPPA = "kappa"


class XyzAxis(str, Enum):
    X = "sam_x"
    Y = "sam_y"
    Z = "sam_z"


class HyperionParameters(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        use_enum_values = True
        extra = Extra.forbid
        json_encoders = {
            ParameterVersion: lambda pv: str(pv),
            NDArray: lambda a: a.tolist(),
        }

    def __hash__(self) -> int:
        return self.json().__hash__()

    parameter_model_version: ParameterVersion

    @validator("parameter_model_version")
    def _validate_version(cls, version: ParameterVersion):
        assert version >= ParameterVersion(
            major=PARAMETER_VERSION.major
        ), f"Parameter version too old! This version of hyperion uses {PARAMETER_VERSION}"
        assert version <= ParameterVersion(
            major=PARAMETER_VERSION.major + 1
        ), f"Parameter version too new! This version of hyperion uses {PARAMETER_VERSION}"
        return version


class DiffractionExperiment(HyperionParameters):
    visit: str = Field(min_length=1)
    file_name: str = Field(pattern=r"[\w]{2}[\d]+-[\d]+")
    exposure_time_s: float = Field(gt=0)
    comment: str = Field(default="")
    beamline: str = Field(default=CONST.I03.BEAMLINE, pattern=r"BL\d{2}[BIJS]")
    insertion_prefix: str = Field(
        default=CONST.I03.INSERTION_PREFIX, pattern=r"SR\d{2}[BIJS]"
    )
    det_dist_to_beam_converter_path: str = Field(
        default=CONST.PARAM.DETECTOR.BEAM_XY_LUT_PATH
    )
    zocalo_environment: str = Field(default=CONST.ZOCALO_ENV)
    detector: str = Field(default=CONST.I03.DETECTOR)
    trigger_mode: TriggerMode = Field(default=TriggerMode.FREE_RUN)
    detector_distance_mm: float | None = Field(default=None, gt=0)
    demand_energy_ev: float | None = Field(default=None, gt=0)
    run_number: int | None = Field(default=None, ge=0)
    storage_directory: str

    @property
    def visit_directory(self) -> Path:
        return (
            Path(CONST.I03.BASE_DATA_DIR) / str(datetime.date.today().year) / self.visit
        )

    @property
    def num_images(self) -> int:
        return 0

    @property
    @abstractmethod
    def detector_params(self) -> DetectorParams: ...

    @property
    @abstractmethod
    def ispyb_params(self) -> IspybParams:  # Soon to remove
        ...


class WithScan(BaseModel):
    @property
    @abstractmethod
    def scan_points(self) -> AxesPoints: ...

    @property
    @abstractmethod
    def num_images(self) -> int: ...


class SplitScan(BaseModel):
    @property
    @abstractmethod
    def scan_indices(self) -> Sequence[SupportsInt]:
        """Should return the first index of each scan (i.e. for each nexus file)"""
        ...


class WithSample(BaseModel):
    sample_id: int  # Will be used to work out puck/pin
    _puck: int | None = None
    _pin: int | None = None


class OptionalXyzStarts(BaseModel):
    x_start_um: float | None = None
    y_start_um: float | None = None
    z_start_um: float | None = None


class XyzStarts(BaseModel):
    x_start_um: float
    y_start_um: float
    z_start_um: float

    def _start_for_axis(self, axis: XyzAxis) -> float:
        match axis:
            case XyzAxis.X:
                return self.x_start_um
            case XyzAxis.Y:
                return self.y_start_um
            case XyzAxis.Z:
                return self.z_start_um


class OptionalGonioAngleStarts(BaseModel):
    omega_start_deg: float | None = None
    phi_start_deg: float | None = None
    chi_start_deg: float | None = None
    kappa_start_deg: float | None = None


class TemporaryIspybExtras(BaseModel):
    # for while we still need ISpyB params - to be removed in #1277 and/or #43
    class Config:
        arbitrary_types_allowed = True
        extra = Extra.forbid

    microns_per_pixel_x: float
    microns_per_pixel_y: float
    position: list[float] | NDArray = Field(default=np.array([0, 0, 0]))
    beam_size_x: float
    beam_size_y: float
    focal_spot_size_x: float
    focal_spot_size_y: float
    resolution: float | None = None
    sample_barcode: str | None = None
    flux: float | None = None
    undulator_gap: float | None = None
    synchrotron_mode: str | None = None
    slit_gap_size_x: float | None = None
    slit_gap_size_y: float | None = None
    xtal_snapshots_omega_start: list[str] | None = None
    xtal_snapshots_omega_end: list[str] | None = None
    xtal_snapshots: list[str] | None = None
    ispyb_experiment_type: str | None = None
    upper_left: list[float] | NDArray | None = None
