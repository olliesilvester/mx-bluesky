"""
Move on click gui for fixed targets at I24
Robin Owen 12 Jan 2021
"""
import logging

import cv2 as cv
from dodal.beamlines import i24
from dodal.devices.oav.oav_detector import OAV

from mx_bluesky.I24.serial.fixed_target import i24ssx_Chip_Manager_py3v1 as manager
from mx_bluesky.I24.serial.fixed_target.ft_utils import Fiducials
from mx_bluesky.I24.serial.parameters.constants import OAV1_CAM

logger = logging.getLogger("I24ssx.moveonclick")

# Set scale.
# TODO See https://github.com/DiamondLightSource/mx_bluesky/issues/44
zoomcalibrator = 6  # 8 seems to work well for zoom 2


def _get_beam_centre(oav: OAV):
    """Extract the beam centre x/y positions from the display.configuration file.

    Args:
        oav (OAV): the OAV device.
    """
    return oav.parameters.beam_centre_i, oav.parameters.beam_centre_j


def get_beam_centre():
    # Get I24 oav device from dodal
    oav = i24.oav()

    beamX, beamY = _get_beam_centre(oav)
    return beamX, beamY


# Register clicks and move chip stages
def onMouse(event, x, y, flags, param):
    pmac = param
    beamX, beamY = get_beam_centre()
    if event == cv.EVENT_LBUTTONUP:
        logger.info("Clicked X and Y %s %s" % (x, y))
        xmove = -1 * (beamX - x) * zoomcalibrator
        ymove = -1 * (beamY - y) * zoomcalibrator
        logger.info("Moving X and Y %s %s" % (xmove, ymove))
        xmovepmacstring = "#1J:" + str(xmove)
        ymovepmacstring = "#2J:" + str(ymove)
        pmac.pmac_string.set(xmovepmacstring)
        pmac.pmac_string.set(ymovepmacstring)


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
    # Get PMAC device
    pmac = i24.pmac()
    # Create a video caputure from OAV1
    cap = cv.VideoCapture(oav1)

    # Create window named OAV1view and set onmouse to this
    cv.namedWindow("OAV1view")
    cv.setMouseCallback("OAV1view", onMouse, param=pmac)  # type: ignore

    logger.info("Showing camera feed. Press escape to close")
    # Read captured video and store them in success and frame
    success, frame = cap.read()

    # Loop until escape key is pressed. Keyboard shortcuts here
    while success:
        success, frame = cap.read()

        update_ui(frame)

        k = cv.waitKey(1)
        if k == 113:  # Q
            manager.moveto(Fiducials.zero, pmac)
        if k == 119:  # W
            manager.moveto(Fiducials.fid1, pmac)
        if k == 101:  # E
            manager.moveto(Fiducials.fid2, pmac)
        if k == 97:  # A
            pmac.home_stages()
            print("Current position set as origin")
        if k == 115:  # S
            manager.fiducial(1)
        if k == 100:  # D
            manager.fiducial(2)
        if k == 99:  # C
            manager.cs_maker(pmac)
        if k == 98:  # B
            manager.block_check()  # doesn't work well for blockcheck as image doesn't update
        if k == 104:  # H
            pmac.pmac_string.set("#2J:-10")
        if k == 110:  # N
            pmac.pmac_string.set("#2J:10")
        if k == 109:  # M
            pmac.pmac_string.set("#1J:-10")
        if k == 98:  # B
            pmac.pmac_string.set("#1J:10")
        if k == 105:  # I
            pmac.pmac_string.set("#3J:-150")
        if k == 111:  # O
            pmac.pmac_string.set("#3J:150")
        if k == 117:  # U
            pmac.pmac_string.set("#3J:-1000")
        if k == 112:  # P
            pmac.pmac_string.set("#3J:-1000")
        if k == 0x1B:  # esc
            cv.destroyWindow("OAV1view")
            print("Pressed escape. Closing window")
            break

    # Clear cameraCapture instance
    cap.release()


if __name__ == "__main__":
    start_viewer()
