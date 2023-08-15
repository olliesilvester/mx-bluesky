from enum import Enum
from pathlib import Path


class SSXType(Enum):
    FIXED = "Serial Fixed"
    EXTRUDER = "Serial Jet"


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
