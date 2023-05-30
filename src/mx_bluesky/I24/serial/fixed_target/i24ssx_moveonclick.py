"""
###################################################
#   Move on click gui for fixed targets at I24    #
####           Robin Owen 12 Jan 2021          ####
#  May need to pip install these for it to run    #
#  opencv-python  Pillow                          #
####################################################
"""

import cv2 as cv

from ..setup_beamline import caput, pv
from . import i24ssx_Chip_Manager_py3v1 as manager

# Set beam position and scale.
beamX = 577
beamY = 409
zoomcalibrator = 6  # 8 seems to work well for zoom 2


# Register clicks and move chip stages
def onMouse(event, x, y, flags, param):
    if event == cv.EVENT_LBUTTONUP:
        print("Clicked X and Y", x, y)
        xmove = -1 * (beamX - x) * zoomcalibrator
        ymove = -1 * (beamY - y) * zoomcalibrator
        print("Moving X and Y", xmove, ymove)
        xmovepmacstring = "#1J:" + str(xmove)
        ymovepmacstring = "#2J:" + str(ymove)
        caput(pv.me14e_pmac_str, xmovepmacstring)
        caput(pv.me14e_pmac_str, ymovepmacstring)


if __name__ == "__main__":
    # Create a video caputure from OAV1
    cap = cv.VideoCapture("http://bl24i-di-serv-01.diamond.ac.uk:8080/OAV1.mjpg.mjpg")

    # Create window named OAV1view and set onmouse to this
    cv.namedWindow("OAV1view")
    cv.setMouseCallback("OAV1view", onMouse)

    print("Showing camera feed. Press escape to close")
    # Read captured video and store them in success and frame
    success, frame = cap.read()

    # Loop until escape key is pressed. Keyboard shortcuts here
    while success:
        success, frame = cap.read()

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
