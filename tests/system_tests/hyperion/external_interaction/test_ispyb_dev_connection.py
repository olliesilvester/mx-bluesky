from __future__ import annotations

import os
import re
from collections.abc import Callable, Sequence
from copy import deepcopy
from decimal import Decimal
from typing import Any, Literal
from unittest.mock import MagicMock, patch

import numpy
import pytest
from bluesky.run_engine import RunEngine
from dodal.devices.oav.oav_parameters import OAVParameters
from dodal.devices.synchrotron import SynchrotronMode
from ophyd.sim import NullStatus
from ophyd_async.core import AsyncStatus, set_mock_value

from mx_bluesky.hyperion.experiment_plans import oav_grid_detection_plan
from mx_bluesky.hyperion.experiment_plans.grid_detect_then_xray_centre_plan import (
    GridDetectThenXRayCentreComposite,
    grid_detect_then_xray_centre,
)
from mx_bluesky.hyperion.experiment_plans.rotation_scan_plan import (
    RotationScanComposite,
    rotation_scan,
)
from mx_bluesky.hyperion.external_interaction.callbacks.common.ispyb_mapping import (
    populate_data_collection_group,
    populate_remaining_data_collection_info,
)
from mx_bluesky.hyperion.external_interaction.callbacks.rotation.ispyb_callback import (
    RotationISPyBCallback,
)
from mx_bluesky.hyperion.external_interaction.callbacks.xray_centre.ispyb_callback import (
    GridscanISPyBCallback,
)
from mx_bluesky.hyperion.external_interaction.callbacks.xray_centre.ispyb_mapping import (
    construct_comment_for_gridscan,
    populate_xy_data_collection_info,
    populate_xz_data_collection_info,
)
from mx_bluesky.hyperion.external_interaction.ispyb.data_model import (
    DataCollectionGridInfo,
    ScanDataInfo,
)
from mx_bluesky.hyperion.external_interaction.ispyb.ispyb_dataclass import Orientation
from mx_bluesky.hyperion.external_interaction.ispyb.ispyb_store import (
    IspybIds,
    StoreInIspyb,
)
from mx_bluesky.hyperion.parameters.components import IspybExperimentType
from mx_bluesky.hyperion.parameters.constants import CONST
from mx_bluesky.hyperion.parameters.gridscan import (
    GridScanWithEdgeDetect,
    ThreeDGridScan,
)
from mx_bluesky.hyperion.parameters.rotation import RotationScan
from mx_bluesky.hyperion.utils.utils import convert_angstrom_to_eV

from ....conftest import fake_read
from .conftest import raw_params_from_file

EXPECTED_DATACOLLECTION_FOR_ROTATION = {
    "wavelength": 0.71,
    "beamSizeAtSampleX": 0.02,
    "beamSizeAtSampleY": 0.02,
    "exposureTime": 0.023,
    "undulatorGap1": 1.12,
    "synchrotronMode": SynchrotronMode.USER.value,
    "slitGapHorizontal": 0.123,
    "slitGapVertical": 0.234,
}

# Map all the case-sensitive column names from their normalised versions
DATA_COLLECTION_COLUMN_MAP = {
    s.lower(): s
    for s in [
        "dataCollectionId",
        "BLSAMPLEID",
        "SESSIONID",
        "experimenttype",
        "dataCollectionNumber",
        "startTime",
        "endTime",
        "runStatus",
        "axisStart",
        "axisEnd",
        "axisRange",
        "overlap",
        "numberOfImages",
        "startImageNumber",
        "numberOfPasses",
        "exposureTime",
        "imageDirectory",
        "imagePrefix",
        "imageSuffix",
        "imageContainerSubPath",
        "fileTemplate",
        "wavelength",
        "resolution",
        "detectorDistance",
        "xBeam",
        "yBeam",
        "comments",
        "printableForReport",
        "CRYSTALCLASS",
        "slitGapVertical",
        "slitGapHorizontal",
        "transmission",
        "synchrotronMode",
        "xtalSnapshotFullPath1",
        "xtalSnapshotFullPath2",
        "xtalSnapshotFullPath3",
        "xtalSnapshotFullPath4",
        "rotationAxis",
        "phiStart",
        "kappaStart",
        "omegaStart",
        "chiStart",
        "resolutionAtCorner",
        "detector2Theta",
        "DETECTORMODE",
        "undulatorGap1",
        "undulatorGap2",
        "undulatorGap3",
        "beamSizeAtSampleX",
        "beamSizeAtSampleY",
        "centeringMethod",
        "averageTemperature",
        "ACTUALSAMPLEBARCODE",
        "ACTUALSAMPLESLOTINCONTAINER",
        "ACTUALCONTAINERBARCODE",
        "ACTUALCONTAINERSLOTINSC",
        "actualCenteringPosition",
        "beamShape",
        "dataCollectionGroupId",
        "POSITIONID",
        "detectorId",
        "FOCALSPOTSIZEATSAMPLEX",
        "POLARISATION",
        "FOCALSPOTSIZEATSAMPLEY",
        "APERTUREID",
        "screeningOrigId",
        "flux",
        "strategySubWedgeOrigId",
        "blSubSampleId",
        "processedDataFile",
        "datFullPath",
        "magnification",
        "totalAbsorbedDose",
        "binning",
        "particleDiameter",
        "boxSize",
        "minResolution",
        "minDefocus",
        "maxDefocus",
        "defocusStepSize",
        "amountAstigmatism",
        "extractSize",
        "bgRadius",
        "voltage",
        "objAperture",
        "c1aperture",
        "c2aperture",
        "c3aperture",
        "c1lens",
        "c2lens",
        "c3lens",
        "startPositionId",
        "endPositionId",
        "flux",
        "bestWilsonPlotPath",
        "totalExposedDose",
        "nominalMagnification",
        "nominalDefocus",
        "imageSizeX",
        "imageSizeY",
        "pixelSizeOnImage",
        "phasePlate",
        "dataCollectionPlanId",
    ]
}

GRID_INFO_COLUMN_MAP = {
    s.lower(): s
    for s in [
        "gridInfoId",
        "dataCollectionGroupId",
        "xOffset",
        "yOffset",
        "dx_mm",
        "dy_mm",
        "steps_x",
        "steps_y",
        "meshAngle",
        "pixelsPerMicronX",
        "pixelsPerMicronY",
        "snapshot_offsetXPixel",
        "snapshot_offsetYPixel",
        "recordTimeStamp",
        "orientation",
        "workflowMeshId",
        "snaked",
        "dataCollectionId",
        "patchesX",
        "patchesY",
        "micronsPerPixelX",
        "micronsPerPixelY",
    ]
}


@pytest.fixture
def dummy_data_collection_group_info(dummy_params):
    return populate_data_collection_group(
        dummy_params,
    )


@pytest.fixture
def dummy_scan_data_info_for_begin(dummy_params):
    info = populate_xy_data_collection_info(
        dummy_params.detector_params,
    )
    info = populate_remaining_data_collection_info(None, None, info, dummy_params)
    return ScanDataInfo(
        data_collection_info=info,
    )


@pytest.fixture
def grid_detect_then_xray_centre_parameters():
    json_dict = raw_params_from_file(
        "tests/test_data/parameter_json_files/ispyb_gridscan_system_test_parameters.json"
    )
    return GridScanWithEdgeDetect(**json_dict)


# noinspection PyUnreachableCode
@pytest.fixture
def grid_detect_then_xray_centre_composite(
    fast_grid_scan,
    backlight,
    smargon,
    undulator,
    synchrotron,
    s4_slit_gaps,
    attenuator,
    xbpm_feedback,
    detector_motion,
    zocalo,
    aperture_scatterguard,
    zebra,
    eiger,
    robot,
    oav,
    dcm,
    flux,
    ophyd_pin_tip_detection,
):
    composite = GridDetectThenXRayCentreComposite(
        zebra_fast_grid_scan=fast_grid_scan,
        pin_tip_detection=ophyd_pin_tip_detection,
        backlight=backlight,
        panda_fast_grid_scan=None,  # type: ignore
        smargon=smargon,
        undulator=undulator,
        synchrotron=synchrotron,
        s4_slit_gaps=s4_slit_gaps,
        attenuator=attenuator,
        xbpm_feedback=xbpm_feedback,
        detector_motion=detector_motion,
        zocalo=zocalo,
        aperture_scatterguard=aperture_scatterguard,
        zebra=zebra,
        eiger=eiger,
        panda=None,  # type: ignore
        robot=robot,
        oav=oav,
        dcm=dcm,
        flux=flux,
    )
    eiger.odin.fan.consumers_connected.sim_put(True)
    eiger.odin.fan.on.sim_put(True)
    eiger.odin.meta.initialised.sim_put(True)
    oav.zoom_controller.zrst.set("1.0x")
    oav.cam.array_size.array_size_x.sim_put(1024)
    oav.cam.array_size.array_size_y.sim_put(768)
    oav.grid_snapshot.x_size.sim_put(1024)
    oav.grid_snapshot.y_size.sim_put(768)
    oav.grid_snapshot.top_left_x.set(50)
    oav.grid_snapshot.top_left_y.set(100)
    oav.grid_snapshot.box_width.set(0.1 * 1000 / 1.25)  # size in pixels
    set_mock_value(undulator.current_gap, 1.11)

    unpatched_method = oav.parameters.load_microns_per_pixel
    eiger.stale_params.sim_put(0)
    eiger.odin.meta.ready.sim_put(1)
    eiger.odin.meta.active.sim_put(1)
    eiger.odin.fan.ready.sim_put(1)

    unpatched_snapshot_trigger = oav.grid_snapshot.trigger

    def mock_snapshot_trigger():
        oav.grid_snapshot.last_path_full_overlay.set("test_1_y")
        oav.grid_snapshot.last_path_outer.set("test_2_y")
        oav.grid_snapshot.last_saved_path.set("test_3_y")
        return unpatched_snapshot_trigger()

    def patch_lmpp(zoom, xsize, ysize):
        unpatched_method(zoom, 1024, 768)

    def mock_pin_tip_detect(_):
        tip_x_px = 100
        tip_y_px = 200
        microns_per_pixel = 2.87  # from zoom levels .xml
        grid_width_px = int(400 / microns_per_pixel)
        target_grid_height_px = 70
        top_edge_data = ([0] * tip_x_px) + (
            [(tip_y_px - target_grid_height_px // 2)] * grid_width_px
        )
        bottom_edge_data = [0] * tip_x_px + [
            (tip_y_px + target_grid_height_px // 2)
        ] * grid_width_px
        set_mock_value(
            ophyd_pin_tip_detection.triggered_top_edge,
            numpy.array(top_edge_data, dtype=numpy.uint32),
        )

        set_mock_value(
            ophyd_pin_tip_detection.triggered_bottom_edge,
            numpy.array(bottom_edge_data, dtype=numpy.uint32),
        )
        set_mock_value(
            zocalo.bbox_sizes, numpy.array([[10, 10, 10]], dtype=numpy.uint64)
        )

        yield from []
        return tip_x_px, tip_y_px

    def mock_set_file_name(val, timeout):
        eiger.odin.meta.file_name.sim_put(val)  # type: ignore
        eiger.odin.file_writer.id.sim_put(val)  # type: ignore
        return NullStatus()

    @AsyncStatus.wrap
    async def mock_complete_status():
        pass

    with (
        patch.object(eiger.odin.nodes, "get_init_state", return_value=True),
        patch.object(eiger, "wait_on_arming_if_started"),
        # xsize, ysize will always be wrong since computed as 0 before we get here
        # patch up load_microns_per_pixel connect to receive non-zero values
        patch.object(
            oav.parameters,
            "load_microns_per_pixel",
            new=MagicMock(side_effect=patch_lmpp),
        ),
        patch.object(
            oav_grid_detection_plan,
            "wait_for_tip_to_be_found",
            side_effect=mock_pin_tip_detect,
        ),
        patch("dodal.devices.areadetector.plugins.MJPG.requests.get"),
        patch("dodal.devices.areadetector.plugins.MJPG.Image.open"),
        patch.object(oav.grid_snapshot, "post_processing"),
        patch.object(oav.grid_snapshot, "trigger", side_effect=mock_snapshot_trigger),
        patch.object(
            eiger.odin.file_writer.file_name,
            "set",
            side_effect=mock_set_file_name,
        ),
        patch.object(fast_grid_scan, "kickoff", return_value=NullStatus()),
        patch.object(fast_grid_scan, "complete", return_value=NullStatus()),
        patch.object(zocalo, "trigger", return_value=NullStatus()),
    ):
        yield composite


def scan_xy_data_info_for_update(
    data_collection_group_id, dummy_params: ThreeDGridScan, scan_data_info_for_begin
):
    scan_data_info_for_update = deepcopy(scan_data_info_for_begin)
    scan_data_info_for_update.data_collection_info.parent_id = data_collection_group_id
    assert dummy_params is not None
    scan_data_info_for_update.data_collection_grid_info = DataCollectionGridInfo(
        dx_in_mm=dummy_params.x_step_size_um,
        dy_in_mm=dummy_params.y_step_size_um,
        steps_x=dummy_params.x_steps,
        steps_y=dummy_params.y_steps,
        microns_per_pixel_x=1.25,
        microns_per_pixel_y=1.25,
        # cast coordinates from numpy int64 to avoid mysql type conversion issues
        snapshot_offset_x_pixel=100,
        snapshot_offset_y_pixel=100,
        orientation=Orientation.HORIZONTAL,
        snaked=True,
    )
    scan_data_info_for_update.data_collection_info.comments = (
        construct_comment_for_gridscan(
            scan_data_info_for_update.data_collection_grid_info,
        )
    )
    return scan_data_info_for_update


def scan_data_infos_for_update_3d(
    ispyb_ids, scan_xy_data_info_for_update, dummy_params: ThreeDGridScan
):
    xz_data_collection_info = populate_xz_data_collection_info(
        dummy_params.detector_params
    )

    assert dummy_params.ispyb_params is not None
    assert dummy_params is not None
    data_collection_grid_info = DataCollectionGridInfo(
        dx_in_mm=dummy_params.x_step_size_um,
        dy_in_mm=dummy_params.z_step_size_um,
        steps_x=dummy_params.x_steps,
        steps_y=dummy_params.z_steps,
        microns_per_pixel_x=1.25,
        microns_per_pixel_y=1.25,
        # cast coordinates from numpy int64 to avoid mysql type conversion issues
        snapshot_offset_x_pixel=100,
        snapshot_offset_y_pixel=50,
        orientation=Orientation.HORIZONTAL,
        snaked=True,
    )
    xz_data_collection_info = populate_remaining_data_collection_info(
        construct_comment_for_gridscan(data_collection_grid_info),
        ispyb_ids.data_collection_group_id,
        xz_data_collection_info,
        dummy_params,
    )
    xz_data_collection_info.parent_id = ispyb_ids.data_collection_group_id

    scan_xz_data_info_for_update = ScanDataInfo(
        data_collection_info=xz_data_collection_info,
        data_collection_grid_info=(data_collection_grid_info),
    )
    return [scan_xy_data_info_for_update, scan_xz_data_info_for_update]


@pytest.fixture
def composite_for_rotation_scan(fake_create_rotation_devices: RotationScanComposite):
    energy_ev = convert_angstrom_to_eV(0.71)
    set_mock_value(
        fake_create_rotation_devices.dcm.energy_in_kev.user_readback,
        energy_ev / 1000,  # pyright: ignore
    )
    set_mock_value(fake_create_rotation_devices.undulator.current_gap, 1.12)  # pyright: ignore
    set_mock_value(
        fake_create_rotation_devices.synchrotron.synchrotron_mode,
        SynchrotronMode.USER,
    )
    set_mock_value(
        fake_create_rotation_devices.synchrotron.top_up_start_countdown,  # pyright: ignore
        -1,
    )
    fake_create_rotation_devices.s4_slit_gaps.xgap.user_readback.sim_put(  # pyright: ignore
        0.123
    )
    fake_create_rotation_devices.s4_slit_gaps.ygap.user_readback.sim_put(  # pyright: ignore
        0.234
    )
    it_snapshot_filenames = iter(
        [
            "/tmp/snapshot1.png",
            "/tmp/snapshot2.png",
            "/tmp/snapshot3.png",
            "/tmp/snapshot4.png",
        ]
    )

    with (
        patch("bluesky.preprocessors.__read_and_stash_a_motor", fake_read),
        patch.object(
            fake_create_rotation_devices.oav.snapshot.last_saved_path, "get"
        ) as mock_last_saved_path,
        patch("bluesky.plan_stubs.wait"),
    ):

        @AsyncStatus.wrap
        async def apply_snapshot_filename():
            mock_last_saved_path.return_value = next(it_snapshot_filenames)

        with patch.object(
            fake_create_rotation_devices.oav.snapshot,
            "trigger",
            side_effect=apply_snapshot_filename,
        ):
            yield fake_create_rotation_devices


@pytest.fixture
def params_for_rotation_scan(test_rotation_params: RotationScan):
    test_rotation_params.rotation_increment_deg = 0.27
    test_rotation_params.exposure_time_s = 0.023
    test_rotation_params.detector_params.expected_energy_ev = 0.71
    return test_rotation_params


@pytest.mark.s03
def test_ispyb_get_comment_from_collection_correctly(fetch_comment: Callable[..., Any]):
    expected_comment_contents = (
        "Xray centring - "
        "Diffraction grid scan of 1 by 41 images, "
        "Top left [454,-4], Bottom right [455,772]"
    )

    assert fetch_comment(8292317) == expected_comment_contents

    assert fetch_comment(2) == ""


@pytest.mark.s03
def test_ispyb_deposition_comment_correct_on_failure(
    dummy_ispyb: StoreInIspyb,
    fetch_comment: Callable[..., Any],
    dummy_data_collection_group_info,
    dummy_scan_data_info_for_begin,
):
    ispyb_ids = dummy_ispyb.begin_deposition(
        dummy_data_collection_group_info, [dummy_scan_data_info_for_begin]
    )
    dummy_ispyb.end_deposition(ispyb_ids, "fail", "could not connect to devices")
    assert (
        fetch_comment(ispyb_ids.data_collection_ids[0])  # type: ignore
        == "DataCollection Unsuccessful reason: could not connect to devices"
    )


@pytest.mark.s03
def test_ispyb_deposition_comment_correct_for_3D_on_failure(
    dummy_ispyb_3d: StoreInIspyb,
    fetch_comment: Callable[..., Any],
    dummy_params,
    dummy_data_collection_group_info,
    dummy_scan_data_info_for_begin,
):
    ispyb_ids = dummy_ispyb_3d.begin_deposition(
        dummy_data_collection_group_info, [dummy_scan_data_info_for_begin]
    )
    scan_data_infos = generate_scan_data_infos(
        dummy_params,
        dummy_scan_data_info_for_begin,
        IspybExperimentType.GRIDSCAN_3D,
        ispyb_ids,
    )
    ispyb_ids = dummy_ispyb_3d.update_deposition(ispyb_ids, scan_data_infos)
    dcid1 = ispyb_ids.data_collection_ids[0]  # type: ignore
    dcid2 = ispyb_ids.data_collection_ids[1]  # type: ignore
    dummy_ispyb_3d.end_deposition(ispyb_ids, "fail", "could not connect to devices")
    assert (
        fetch_comment(dcid1)
        == "Hyperion: Xray centring - Diffraction grid scan of 40 by 20 images in 100.0 um by 100.0 um steps. Top left (px): [100,100], bottom right (px): [3300,1700]. DataCollection Unsuccessful reason: could not connect to devices"
    )
    assert (
        fetch_comment(dcid2)
        == "Hyperion: Xray centring - Diffraction grid scan of 40 by 10 images in 100.0 um by 100.0 um steps. Top left (px): [100,50], bottom right (px): [3300,850]. DataCollection Unsuccessful reason: could not connect to devices"
    )


@pytest.mark.s03
@pytest.mark.parametrize(
    "experiment_type, exp_num_of_grids, success",
    [
        (IspybExperimentType.GRIDSCAN_2D, 1, False),
        (IspybExperimentType.GRIDSCAN_2D, 1, True),
        (IspybExperimentType.GRIDSCAN_3D, 2, False),
        (IspybExperimentType.GRIDSCAN_3D, 2, True),
    ],
)
def test_can_store_2D_ispyb_data_correctly_when_in_error(
    experiment_type,
    exp_num_of_grids: Literal[1, 2],
    success: bool,
    fetch_comment: Callable[..., Any],
    dummy_params,
    dummy_data_collection_group_info,
    dummy_scan_data_info_for_begin,
):
    ispyb: StoreInIspyb = StoreInIspyb(CONST.SIM.DEV_ISPYB_DATABASE_CFG)
    ispyb_ids: IspybIds = ispyb.begin_deposition(
        dummy_data_collection_group_info, [dummy_scan_data_info_for_begin]
    )
    scan_data_infos = generate_scan_data_infos(
        dummy_params, dummy_scan_data_info_for_begin, experiment_type, ispyb_ids
    )

    ispyb_ids = ispyb.update_deposition(ispyb_ids, scan_data_infos)
    assert len(ispyb_ids.data_collection_ids) == exp_num_of_grids  # type: ignore
    assert len(ispyb_ids.grid_ids) == exp_num_of_grids  # type: ignore
    assert isinstance(ispyb_ids.data_collection_group_id, int)

    expected_comments = [
        (
            "Hyperion: Xray centring - Diffraction grid scan of 40 by 20 "
            "images in 100.0 um by 100.0 um steps. Top left (px): [100,100], bottom right (px): [3300,1700]."
        ),
        (
            "Hyperion: Xray centring - Diffraction grid scan of 40 by 10 "
            "images in 100.0 um by 100.0 um steps. Top left (px): [100,50], bottom right (px): [3300,850]."
        ),
    ]

    if success:
        ispyb.end_deposition(ispyb_ids, "success", "")
    else:
        ispyb.end_deposition(ispyb_ids, "fail", "In error")
        expected_comments = [
            e + " DataCollection Unsuccessful reason: In error"
            for e in expected_comments
        ]

    assert (
        not isinstance(ispyb_ids.data_collection_ids, int)
        and ispyb_ids.data_collection_ids is not None
    )
    for grid_no, dc_id in enumerate(ispyb_ids.data_collection_ids):
        assert fetch_comment(dc_id) == expected_comments[grid_no]


@pytest.mark.s03
def test_ispyb_deposition_in_gridscan(
    RE: RunEngine,
    grid_detect_then_xray_centre_composite: GridDetectThenXRayCentreComposite,
    grid_detect_then_xray_centre_parameters: GridScanWithEdgeDetect,
    fetch_datacollection_attribute: Callable[..., Any],
    fetch_datacollection_grid_attribute: Callable[..., Any],
    fetch_datacollection_position_attribute: Callable[..., Any],
):
    os.environ["ISPYB_CONFIG_PATH"] = CONST.SIM.DEV_ISPYB_DATABASE_CFG
    grid_detect_then_xray_centre_composite.s4_slit_gaps.xgap.user_readback.sim_put(0.1)  # type: ignore
    grid_detect_then_xray_centre_composite.s4_slit_gaps.ygap.user_readback.sim_put(0.1)  # type: ignore
    ispyb_callback = GridscanISPyBCallback()
    RE.subscribe(ispyb_callback)
    RE(
        grid_detect_then_xray_centre(
            grid_detect_then_xray_centre_composite,
            grid_detect_then_xray_centre_parameters,
        )
    )

    ispyb_ids = ispyb_callback.ispyb_ids
    DC_EXPECTED_VALUES = {
        "detectorid": 78,
        "axisstart": 0.0,
        "axisrange": 0,
        "axisend": 0,
        "focalspotsizeatsamplex": 0.02,
        "focalspotsizeatsampley": 0.02,
        "slitgapvertical": 0.1,
        "slitgaphorizontal": 0.1,
        "beamsizeatsamplex": 0.02,
        "beamsizeatsampley": 0.02,
        "transmission": 49.118,
        "datacollectionnumber": 1,
        "detectordistance": 100.0,
        "exposuretime": 0.12,
        "imagedirectory": "/tmp/",
        "imageprefix": "file_name",
        "imagesuffix": "h5",
        "numberofpasses": 1,
        "overlap": 0,
        "omegastart": 0,
        "startimagenumber": 1,
        "wavelength": 0.976254,
        "xbeam": 150.0,
        "ybeam": 160.0,
        "xtalsnapshotfullpath1": "test_1_y",
        "xtalsnapshotfullpath2": "test_2_y",
        "xtalsnapshotfullpath3": "test_3_y",
        "synchrotronmode": "User",
        "undulatorgap1": 1.11,
        "filetemplate": "file_name_1_master.h5",
        "numberofimages": 20 * 12,
    }
    compare_comment(
        fetch_datacollection_attribute,
        ispyb_ids.data_collection_ids[0],
        "Hyperion: Xray centring - Diffraction grid scan of 20 by 12 "
        "images in 20.0 um by 20.0 um steps. Top left (px): [100,161], "
        "bottom right (px): [239,244]. Aperture: Small. ",
    )
    compare_actual_and_expected(
        ispyb_ids.data_collection_ids[0],
        DC_EXPECTED_VALUES,
        fetch_datacollection_attribute,
        DATA_COLLECTION_COLUMN_MAP,
    )
    GRIDINFO_EXPECTED_VALUES = {
        "gridInfoId": ispyb_ids.grid_ids[0],
        "dx_mm": 0.02,
        "dy_mm": 0.02,
        "steps_x": 20,
        "steps_y": 12,
        "snapshot_offsetXPixel": 100,
        "snapshot_offsetYPixel": 161,
        "orientation": "horizontal",
        "snaked": True,
        "dataCollectionId": ispyb_ids.data_collection_ids[0],
        "micronsPerPixelX": 2.87,
        "micronsPerPixelY": 2.87,
    }

    compare_actual_and_expected(
        ispyb_ids.grid_ids[0],
        GRIDINFO_EXPECTED_VALUES,
        fetch_datacollection_grid_attribute,
        GRID_INFO_COLUMN_MAP,
    )
    position_id = fetch_datacollection_attribute(
        ispyb_ids.data_collection_ids[0], DATA_COLLECTION_COLUMN_MAP["positionid"]
    )
    assert position_id is None
    DC_EXPECTED_VALUES.update(
        {
            "axisstart": 90.0,
            "axisend": 90.0,
            "datacollectionnumber": 2,
            "omegastart": 90.0,
            "filetemplate": "file_name_2_master.h5",
            "numberofimages": 220,
        }
    )
    compare_actual_and_expected(
        ispyb_ids.data_collection_ids[1],
        DC_EXPECTED_VALUES,
        fetch_datacollection_attribute,
        DATA_COLLECTION_COLUMN_MAP,
    )
    compare_comment(
        fetch_datacollection_attribute,
        ispyb_ids.data_collection_ids[1],
        "Hyperion: Xray centring - Diffraction grid scan of 20 by 11 "
        "images in 20.0 um by 20.0 um steps. Top left (px): [100,165], "
        "bottom right (px): [239,241]. Aperture: Small. ",
    )
    position_id = fetch_datacollection_attribute(
        ispyb_ids.data_collection_ids[1], DATA_COLLECTION_COLUMN_MAP["positionid"]
    )
    assert position_id is None
    GRIDINFO_EXPECTED_VALUES.update(
        {
            "gridInfoId": ispyb_ids.grid_ids[1],
            "steps_y": 11.0,
            "snapshot_offsetYPixel": 165.0,
            "dataCollectionId": ispyb_ids.data_collection_ids[1],
        }
    )
    compare_actual_and_expected(
        ispyb_ids.grid_ids[1],
        GRIDINFO_EXPECTED_VALUES,
        fetch_datacollection_grid_attribute,
        GRID_INFO_COLUMN_MAP,
    )


@pytest.mark.s03
def test_ispyb_deposition_in_rotation_plan(
    composite_for_rotation_scan: RotationScanComposite,
    params_for_rotation_scan: RotationScan,
    oav_parameters_for_rotation: OAVParameters,
    RE: RunEngine,
    fetch_comment: Callable[..., Any],
    fetch_datacollection_attribute: Callable[..., Any],
    fetch_datacollectiongroup_attribute: Callable[..., Any],
    fetch_datacollection_position_attribute: Callable[..., Any],
):
    os.environ["ISPYB_CONFIG_PATH"] = CONST.SIM.DEV_ISPYB_DATABASE_CFG
    ispyb_cb = RotationISPyBCallback()
    RE.subscribe(ispyb_cb)

    RE(
        rotation_scan(
            composite_for_rotation_scan,
            params_for_rotation_scan,
            oav_parameters_for_rotation,
        )
    )

    dcid = ispyb_cb.ispyb_ids.data_collection_ids[0]
    assert dcid is not None
    assert (
        fetch_comment(dcid)
        == "Sample position (µm): (1000, 2000, 3000) test  Aperture: Small. "
    )

    expected_values = EXPECTED_DATACOLLECTION_FOR_ROTATION | {
        "xtalSnapshotFullPath1": "/tmp/snapshot1.png",
        "xtalSnapshotFullPath2": "/tmp/snapshot2.png",
        "xtalSnapshotFullPath3": "/tmp/snapshot3.png",
        "xtalSnapshotFullPath4": "/tmp/snapshot4.png",
    }

    compare_actual_and_expected(dcid, expected_values, fetch_datacollection_attribute)

    position_id = fetch_datacollection_attribute(
        dcid, DATA_COLLECTION_COLUMN_MAP["positionid"]
    )
    expected_values = {"posX": 1.0, "posY": 2.0, "posZ": 3.0}
    compare_actual_and_expected(
        position_id, expected_values, fetch_datacollection_position_attribute
    )


@pytest.mark.s03
def test_ispyb_deposition_in_rotation_plan_snapshots_in_parameters(
    composite_for_rotation_scan: RotationScanComposite,
    params_for_rotation_scan: RotationScan,
    oav_parameters_for_rotation: OAVParameters,
    RE: RunEngine,
    fetch_datacollection_attribute: Callable[..., Any],
):
    os.environ["ISPYB_CONFIG_PATH"] = CONST.SIM.DEV_ISPYB_DATABASE_CFG
    ispyb_cb = RotationISPyBCallback()
    RE.subscribe(ispyb_cb)
    params_for_rotation_scan.snapshot_omegas_deg = None
    params_for_rotation_scan.ispyb_extras.xtal_snapshots_omega_start = [  # type: ignore
        "/tmp/test_snapshot1.png",
        "/tmp/test_snapshot2.png",
        "/tmp/test_snapshot3.png",
    ]
    RE(
        rotation_scan(
            composite_for_rotation_scan,
            params_for_rotation_scan,
            oav_parameters_for_rotation,
        )
    )

    dcid = ispyb_cb.ispyb_ids.data_collection_ids[0]
    assert dcid is not None
    expected_values = EXPECTED_DATACOLLECTION_FOR_ROTATION | {
        "xtalSnapshotFullPath1": "/tmp/test_snapshot1.png",
        "xtalSnapshotFullPath2": "/tmp/test_snapshot2.png",
        "xtalSnapshotFullPath3": "/tmp/test_snapshot3.png",
    }

    compare_actual_and_expected(dcid, expected_values, fetch_datacollection_attribute)


def generate_scan_data_infos(
    dummy_params,
    dummy_scan_data_info_for_begin: ScanDataInfo,
    experiment_type: IspybExperimentType,
    ispyb_ids: IspybIds,
) -> Sequence[ScanDataInfo]:
    xy_scan_data_info = scan_xy_data_info_for_update(
        ispyb_ids.data_collection_group_id, dummy_params, dummy_scan_data_info_for_begin
    )
    xy_scan_data_info.data_collection_id = ispyb_ids.data_collection_ids[0]
    if experiment_type == IspybExperimentType.GRIDSCAN_3D:
        scan_data_infos = scan_data_infos_for_update_3d(
            ispyb_ids, xy_scan_data_info, dummy_params
        )
    else:
        scan_data_infos = [xy_scan_data_info]
    return scan_data_infos


def compare_actual_and_expected(
    id, expected_values, fetch_datacollection_attribute, column_map: dict | None = None
):
    results = "\n"
    for k, v in expected_values.items():
        actual = fetch_datacollection_attribute(
            id, column_map[k.lower()] if column_map else k
        )
        if isinstance(actual, Decimal):
            actual = float(actual)
        if isinstance(v, float):
            actual_v = actual == pytest.approx(v)
        else:
            actual_v = actual == v
        if not actual_v:
            results += f"expected {k} {v} == {actual}\n"
    assert results == "\n", results


def compare_comment(
    fetch_datacollection_attribute, data_collection_id, expected_comment
):
    actual_comment = fetch_datacollection_attribute(
        data_collection_id, DATA_COLLECTION_COLUMN_MAP["comments"]
    )
    match = re.search(" Zocalo processing took", actual_comment)
    truncated_comment = actual_comment[: match.start()] if match else actual_comment
    assert truncated_comment == expected_comment
