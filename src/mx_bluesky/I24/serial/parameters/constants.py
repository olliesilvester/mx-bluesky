from enum import Enum


class SSXType(Enum):
    FIXED = "Serial Fixed"
    EXTRUDER = "Serial Jet"


PARAM_FILE_PATH = "src/mx_bluesky/I24/serial/parameters/"
LITEMAP_PATH = "src/mx_bluesky/I24/serial/parameters/litemaps"
FULLMAP_PATH = "src/mx_bluesky/I24/serial/parameters/fullmaps"


PVAR_FILE_PATH = (
    "/dls_sw/work/R3.14.12.3/ioc/ME14E/ME14E-MO-IOC-01/ME14E-MO-IOC-01App/scripts/"
)
"""
Just for reference, original locations:
# "/dls_sw/i24/scripts/extruder/"
# "/dls_sw/i24/scripts/fastchips/parameter_files/"
# "/dls_sw/i24/scripts/fastchips/litemaps/"
# or '/localhome/local/Documents/sacla/parameter_files/' for the last 2
# "/dls_sw/i24/scripts/fastchips/fullmaps/"
"""
