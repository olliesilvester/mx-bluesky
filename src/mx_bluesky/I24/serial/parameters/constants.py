from enum import Enum
from pathlib import Path


class SSXType(Enum):
    FIXED = "Serial Fixed"
    EXTRUDER = "Serial Jet"


PARAM_FILE_PATH = Path("src/mx_bluesky/I24/serial/parameters")
PARAM_FILE_PATH_FT = Path("src/mx_bluesky/I24/serial/parameters/fixed_target")
LITEMAP_PATH = Path("src/mx_bluesky/I24/serial/parameters/fixed_target/litemaps")
FULLMAP_PATH = Path("src/mx_bluesky/I24/serial/parameters/fixed_target/fullmaps")
PVAR_FILE_PATH = Path("src/mx_bluesky/I24/serial/parameters/pvar_files")
HEADER_FILES_PATH = Path("/dls_sw/i24/scripts/fastchips/")
CS_FILES_PATH = Path("src/mx_bluesky/I24/serial/parameters/fixed_target/cs")
