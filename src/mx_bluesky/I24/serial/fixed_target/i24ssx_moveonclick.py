"""
Move on click gui for fixed targets at I24
Robin Owen 12 Jan 2021
"""
import logging
from typing import Dict

import cv2 as cv
from dodal.devices.oav.oav_parameters import OAVParameters

from mx_bluesky.I24.serial.fixed_target import i24ssx_Chip_Manager_py3v1 as manager
from mx_bluesky.I24.serial.parameters.constants import OAV1_CAM, OAV_CONFIG_FILES
from mx_bluesky.I24.serial.setup_beamline import caput, pv

logger = logging.getLogger("I24ssx.moveonclick")

# Set scale.
# TODO See https://github.com/DiamondLightSource/mx_bluesky/issues/44
zoomcalibrator = 6  # 8 seems to work well for zoom 2


def _get_beam_centre(oav_params: OAVParameters):
    """Extract the beam centre x/y positions from the display.configuration file.

    Args:
        oav_params (OAVParamters): the OAV parameters.
    """
    # Set to 1.0, as this is the only value that is updated in display config
    # on the beamline (all other beam positions will be invalid)
    beamX, beamY = oav_params.get_beam_position_from_zoom(1.0)
    return beamX, beamY


# TODO In the future, this should be done automatically in the OAV device
# See https://github.com/DiamondLightSource/dodal/issues/224
def get_beam_centre(oav_config: Dict = OAV_CONFIG_FILES):
    # Get I24 oav parameters from dodal
    # Use xraycentering as context, not super relevant here.
    oav_params = OAVParameters("xrayCentring", **oav_config)

    return _get_beam_centre(oav_params)


# Register clicks and move chip stages
def onMouse(event, x, y, flags, param):
    beamX, beamY = get_beam_centre()
    if event == cv.EVENT_LBUTTONUP:
        logger.info("Clicked X and Y %s %s" % (x, y))
        xmove = -1 * (beamX - x) * zoomcalibrator
        ymove = 1 * (beamY - y) * zoomcalibrator
        logger.info("Moving X and Y %s %s" % (xmove, ymove))
        xmovepmacstring = "#1J:" + str(xmove)
        ymovepmacstring = "#2J:" + str(ymove)
        caput(pv.me14e_pmac_str, xmovepmacstring)
        caput(pv.me14e_pmac_str, ymovepmacstring)


def update_ui(frame):
    # Get beam x and y values
    beamX, beamY = get_beam_centre()

    # Overlay text and beam centre
    cv.ellipse(
        frame, (beamX, beamY), (12, 8), 0.0, 0.0, 360, (0, 255, 255), thickness=2
    )
    # putText(frame,'text',bottomLeftCornerOfText, font, fontScale, fontColor, thickness, lineType)
    cv.putText(
        frame,
        "Key bindings",
        (20, 40),
        cv.FONT_HERSHEY_COMPLEX_SMALL,
        1,
        (0, 255, 255),
        1,
        1,
    )
    cv.putText(
        frame,
        "Q / A : go to / set as f0",
        (25, 70),
        cv.FONT_HERSHEY_COMPLEX_SMALL,
        0.8,
        (0, 255, 255),
        1,
        1,
    )
    cv.putText(
        frame,
        "W / S : go to / set as f1",
        (25, 90),
        cv.FONT_HERSHEY_COMPLEX_SMALL,
        0.8,
        (0, 255, 255),
        1,
        1,
    )
    cv.putText(
        frame,
        "E / D : go to / set as f2",
        (25, 110),
        cv.FONT_HERSHEY_COMPLEX_SMALL,
        0.8,
        (0, 255, 255),
        1,
        1,
    )
    cv.putText(
        frame,
        "I / O : in /out of focus",
        (25, 130),
        cv.FONT_HERSHEY_COMPLEX_SMALL,
        0.8,
        (0, 255, 255),
        1,
        1,
    )
    cv.putText(
        frame,
        "C : Create CS",
        (25, 150),
        cv.FONT_HERSHEY_COMPLEX_SMALL,
        0.8,
        (0, 255, 255),
        1,
        1,
    )
    cv.putText(
        frame,
        "esc : close window",
        (25, 170),
        cv.FONT_HERSHEY_COMPLEX_SMALL,
        0.8,
        (0, 255, 255),
        1,
        1,
    )
    cv.imshow("OAV1view", frame)


def start_viewer(oav1: str = OAV1_CAM):
    # Create a video caputure from OAV1
    cap = cv.VideoCapture(oav1)

    # Create window named OAV1view and set onmouse to this
    cv.namedWindow("OAV1view")
    cv.setMouseCallback("OAV1view", onMouse)  # type: ignore

    logger.info("Showing camera feed. Press escape to close")
    # Read captured video and store them in success and frame
    success, frame = cap.read()

    # Loop until escape key is pressed. Keyboard shortcuts here
    while success:
        success, frame = cap.read()

        update_ui(frame)

        k = cv.waitKey(1)
        if k == 113:  # Q
            manager.moveto("zero")
        if k == 119:  # W
            manager.moveto("f1")
        if k == 101:  # E
            manager.moveto("f2")
        if k == 97:  # A
            caput(pv.me14e_pmac_str, r"\#1hmz\#2hmz\#3hmz")
            print("Current position set as origin")
        if k == 115:  # S
            manager.fiducial(1)
        if k == 100:  # D
            manager.fiducial(2)
        if k == 99:  # C
            manager.cs_maker()
        if k == 98:  # B
            manager.block_check()  # doesn't work well for blockcheck as image doesn't update
        if k == 104:  # H
            caput(pv.me14e_pmac_str, "#2J:-10")
        if k == 110:  # N
            caput(pv.me14e_pmac_str, "#2J:10")
        if k == 109:  # M
            caput(pv.me14e_pmac_str, "#1J:-10")
        if k == 98:  # B
            caput(pv.me14e_pmac_str, "#1J:10")
        if k == 105:  # I
            caput(pv.me14e_pmac_str, "#3J:-150")
        if k == 111:  # O
            caput(pv.me14e_pmac_str, "#3J:150")
        if k == 117:  # U
            caput(pv.me14e_pmac_str, "#3J:-1000")
        if k == 112:  # P
            caput(pv.me14e_pmac_str, "#3J:1000")
        if k == 0x1B:  # esc
            cv.destroyWindow("OAV1view")
            print("Pressed escape. Closing window")
            break

    # Clear cameraCapture instance
    cap.release()


if __name__ == "__main__":
    start_viewer()
