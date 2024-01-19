from enum import Enum
from pathlib import Path


class SSXType(Enum):
    FIXED = "Serial Fixed"
    EXTRUDER = "Serial Jet"


OAV_CONFIG_FILES = {
    "zoom_params_file": "/dls_sw/i24/software/gda/config/xml/jCameraManZoomLevels.xml",
    "oav_config_json": "/dls_sw/i24/software/daq_configuration/json/OAVCentring.json",
    "display_config": "/dls_sw/i24/software/gda_versions/var/display.configuration",
}
OAV1_CAM = "http://bl24i-di-serv-01.diamond.ac.uk:8080/OAV1.mjpg.mjpg"

HEADER_FILES_PATH = Path("/dls_sw/i24/scripts/fastchips/").expanduser().resolve()

PARAM_FILE_PATH = Path(__file__).absolute().parent
PARAM_FILE_PATH_FT = PARAM_FILE_PATH / "fixed_target"
LITEMAP_PATH = PARAM_FILE_PATH_FT / "litemaps"
FULLMAP_PATH = PARAM_FILE_PATH_FT / "fullmaps"
PVAR_FILE_PATH = PARAM_FILE_PATH_FT / "pvar_files"
CS_FILES_PATH = PARAM_FILE_PATH_FT / "cs"
