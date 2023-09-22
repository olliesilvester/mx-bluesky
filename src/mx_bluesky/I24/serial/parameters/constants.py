from pathlib import Path

OAV_CONFIG_FILES = {
    "zoom_params_file": "/dls_sw/i24/software/gda/config/xml/jCameraManZoomLevels.xml",
    "oav_config_json": "/dls_sw/i24/software/daq_configuration/json/OAVCentring.json",
    "display_config": "/dls_sw/i24/software/gda_versions/var/display.configuration",
}

PARAM_FILE_PATH = Path("src/mx_bluesky/I24/serial/parameters").expanduser().resolve()
PARAM_FILE_PATH_FT = (
    Path("src/mx_bluesky/I24/serial/parameters/fixed_target").expanduser().resolve()
)
LITEMAP_PATH = (
    Path("src/mx_bluesky/I24/serial/parameters/fixed_target/litemaps")
    .expanduser()
    .resolve()
)
FULLMAP_PATH = (
    Path("src/mx_bluesky/I24/serial/parameters/fixed_target/fullmaps")
    .expanduser()
    .resolve()
)
PVAR_FILE_PATH = (
    Path("src/mx_bluesky/I24/serial/parameters/fixed_target/pvar_files")
    .expanduser()
    .resolve()
)
HEADER_FILES_PATH = Path("/dls_sw/i24/scripts/fastchips/").expanduser().resolve()
CS_FILES_PATH = (
    Path("src/mx_bluesky/I24/serial/parameters/fixed_target/cs").expanduser().resolve()
)
