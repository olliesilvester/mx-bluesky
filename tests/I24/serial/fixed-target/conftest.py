import json
import tempfile

import pytest

test_display_config = """zoomLevel = 1.0
crosshairX = 475
crosshairY = 309
topLeftX = 614
topLeftY = 444
bottomRightX = 634
bottomRightY = 464
zoomLevel = 2.0
crosshairX = 638
crosshairY = 392
topLeftX = 614
topLeftY = 444
bottomRightX = 634
bottomRightY = 464
zoomLevel = 3.0
crosshairX = 638
crosshairY = 392
topLeftX = 614
topLeftY = 444
bottomRightX = 634
bottomRightY = 464
"""


@pytest.fixture
def dummy_jCameraSettings():
    test_jCamera = """<?xml version="1.0" encoding="UTF-8"?>
        <JCameraManSettings>
        <levels>
            <zoomLevel>
                <level>1</level>
                <position>1.0</position>
                <micronsPerXPixel>1.546</micronsPerXPixel>
                <micronsPerYPixel>1.546</micronsPerYPixel>
            </zoomLevel>
            <zoomLevel>
                <level>2</level>
                <position>20.0</position>
                <micronsPerXPixel>0.999</micronsPerXPixel>
                <micronsPerYPixel>0.999</micronsPerYPixel>
            </zoomLevel>
            <zoomLevel>
                <level>3</level>
                <position>30.0</position>
                <micronsPerXPixel>0.749</micronsPerXPixel>
                <micronsPerYPixel>0.749</micronsPerYPixel>
            </zoomLevel>
        </levels>
        <tolerance>1.0</tolerance>
        </JCameraManSettings>
    """
    test_xml_file = tempfile.NamedTemporaryFile(suffix=".xml", delete=True)
    with open(test_xml_file.name, "w") as f:
        f.write(test_jCamera)
    yield test_xml_file


@pytest.fixture
def dummy_display_config():
    test_config_file = tempfile.NamedTemporaryFile(suffix=".configuration", delete=True)
    with open(test_config_file.name, "w") as f:
        f.write(test_display_config)
    yield test_config_file


@pytest.fixture
def dummy_oav_config():
    test_oav_config = {
        "exposure": 0.004,
        "acqPeriod": 0.1,
        "gain": 1.0,
        "minheight": 5,
        "oav": "OAV1",
        "mxsc_input": "CAM",
        "min_callback_time": 0.5,
        "close_ksize": 11,
        "direction": 3,
        "xrayCentring": {
            "zoom": 2.0,
            "preprocess": 8,
            "preProcessKSize": 30,
            "CannyEdgeUpperThreshold": 10.0,
            "CannyEdgeLowerThreshold": 5.0,
            "brightness": 50,
        },
    }
    test_oav_file = tempfile.NamedTemporaryFile(suffix=".json", delete=True)
    with open(test_oav_file.name, "w") as f:
        json.dump(test_oav_config, f, indent=4)
    yield test_oav_file
