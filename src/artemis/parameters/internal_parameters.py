import artemis.experiment_plans.experiment_registry as registry
from artemis.devices.det_dim_constants import constants_from_type
from artemis.devices.eiger import DETECTOR_PARAM_DEFAULTS, DetectorParams
from artemis.external_interaction.ispyb.ispyb_dataclass import (
    ISPYB_PARAM_DEFAULTS,
    IspybParams,
)
from artemis.log import LOGGER
from artemis.parameters.constants import (
    SIM_BEAMLINE,
    SIM_INSERTION_PREFIX,
    SIM_ZOCALO_ENV,
)
from artemis.parameters.external_parameters import RawParameters
from artemis.utils import Point3D


class ArtemisParameters:
    zocalo_environment: str = SIM_ZOCALO_ENV
    beamline: str = SIM_BEAMLINE
    insertion_prefix: str = SIM_INSERTION_PREFIX
    experiment_type: str = registry.EXPERIMENT_NAMES[0]
    detector_params: DetectorParams = DetectorParams(**DETECTOR_PARAM_DEFAULTS)

    ispyb_params: IspybParams = IspybParams(**ISPYB_PARAM_DEFAULTS)

    def __init__(
        self,
        zocalo_environment: str = SIM_ZOCALO_ENV,
        beamline: str = SIM_BEAMLINE,
        insertion_prefix: str = SIM_INSERTION_PREFIX,
        experiment_type: str = registry.EXPERIMENT_NAMES[0],
        detector_params: DetectorParams = DetectorParams(**DETECTOR_PARAM_DEFAULTS),
        ispyb_params: IspybParams = IspybParams(**ISPYB_PARAM_DEFAULTS),
    ) -> None:
        self.zocalo_environment = zocalo_environment
        self.beamline = beamline
        self.insertion_prefix = insertion_prefix
        self.experiment_type = experiment_type
        self.detector_params = detector_params
        self.ispyb_params = ispyb_params

    def __eq__(self, other) -> bool:
        if not isinstance(other, ArtemisParameters):
            return NotImplemented
        elif self.zocalo_environment != other.zocalo_environment:
            return False
        elif self.beamline != other.beamline:
            return False
        elif self.insertion_prefix != other.insertion_prefix:
            return False
        elif self.experiment_type != other.experiment_type:
            return False
        elif self.detector_params != other.detector_params:
            return False
        elif self.ispyb_params != other.ispyb_params:
            return False
        return True


class InternalParameters:
    artemis_params: ArtemisParameters
    experiment_params: registry.EXPERIMENT_TYPES

    def __init__(self, external_params: RawParameters = RawParameters()):
        self.artemis_params = ArtemisParameters(
            **external_params.artemis_params.to_dict()
        )
        self.artemis_params.detector_params = DetectorParams(
            **self.artemis_params.detector_params
        )
        self.artemis_params.detector_params.detector_size_constants = (
            constants_from_type(
                self.artemis_params.detector_params.detector_size_constants
            )
        )
        self.artemis_params.ispyb_params = IspybParams(
            **self.artemis_params.ispyb_params
        )
        LOGGER.info(f"Upper left before {self.artemis_params.ispyb_params.upper_left} ")
        self.artemis_params.ispyb_params.upper_left = Point3D(
            **self.artemis_params.ispyb_params.upper_left
        )
        LOGGER.info(f"Upper left after {self.artemis_params.ispyb_params.upper_left}")
        self.artemis_params.ispyb_params.position = Point3D(
            **self.artemis_params.ispyb_params.position
        )
        self.experiment_params = registry.EXPERIMENT_TYPE_DICT[
            ArtemisParameters.experiment_type
        ](**external_params.experiment_params.to_dict())

    def __eq__(self, other) -> bool:
        if not isinstance(other, InternalParameters):
            return NotImplemented
        if self.artemis_params != other.artemis_params:
            return False
        if self.experiment_params != other.experiment_params:
            return False
        return True

    @classmethod
    def from_external_json(cls, json_data):
        """Convenience method to generate from external parameter JSON blob, uses
        RawParameters.from_json()"""
        return cls(RawParameters.from_json(json_data))

    @classmethod
    def from_external_dict(cls, dict_data):
        """Convenience method to generate from external parameter dictionary, uses
        RawParameters.from_dict()"""
        return cls(RawParameters.from_dict(dict_data))
