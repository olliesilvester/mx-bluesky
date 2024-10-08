from __future__ import annotations

from mx_bluesky.hyperion.external_interaction.ispyb.data_model import DataCollectionInfo
from mx_bluesky.hyperion.log import ISPYB_LOGGER
from mx_bluesky.hyperion.parameters.rotation import RotationScan


def populate_data_collection_info_for_rotation(params: RotationScan):
    info = DataCollectionInfo(
        omega_start=params.omega_start_deg,
        data_collection_number=params.detector_params.run_number,  # type:ignore # the validator always makes this int
        n_images=params.num_images,
        axis_range=params.rotation_increment_deg,
        axis_start=params.omega_start_deg,
        axis_end=(params.omega_start_deg + params.scan_width_deg),
        kappa_start=params.kappa_start_deg,
    )
    (
        info.xtal_snapshot1,
        info.xtal_snapshot2,
        info.xtal_snapshot3,
        info.xtal_snapshot4,
    ) = get_xtal_snapshots(params.ispyb_params)
    return info


def get_xtal_snapshots(ispyb_params):
    if ispyb_params.xtal_snapshots_omega_start:
        xtal_snapshots = ispyb_params.xtal_snapshots_omega_start[:4]
        ISPYB_LOGGER.info(
            f"Using rotation scan snapshots {xtal_snapshots} for ISPyB deposition"
        )
    else:
        ISPYB_LOGGER.warning("No xtal snapshot paths sent to ISPyB!")
        xtal_snapshots = []
    return xtal_snapshots + [None] * (4 - len(xtal_snapshots))
