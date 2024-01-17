from typing import Tuple
from unittest.mock import ANY, MagicMock, call, patch

import cv2 as cv
import pytest
from dodal.devices.i24.pmac import PMAC

from mx_bluesky.I24.serial.fixed_target.i24ssx_moveonclick import (
    onMouse,
    update_ui,
)


@pytest.mark.parametrize(
    "beam_position, expected_xmove, expected_ymove",
    [
        ((15, 10), "#1J:-90", "#2J:-60"),
        ((100, 150), "#1J:-600", "#2J:-900"),
        ((475, 309), "#1J:-2850", "#2J:-1854"),
        ((638, 392), "#1J:-3828", "#2J:-2352"),
    ],
)
@patch("mx_bluesky.I24.serial.fixed_target.i24ssx_moveonclick.i24.pmac", autospec=True)
@patch("mx_bluesky.I24.serial.fixed_target.i24ssx_moveonclick.get_beam_centre")
def test_onMouse_gets_beam_position_and_sends_correct_str(
    fake_get_beam_pos: MagicMock,
    fake_pmac: PMAC,
    beam_position: Tuple,
    expected_xmove: str,
    expected_ymove: str,
):
    fake_get_beam_pos.side_effect = [beam_position]
    fake_pmac.pmac_string = MagicMock()
    onMouse(cv.EVENT_LBUTTONUP, 0, 0, "", param=fake_pmac)
    fake_pmac.pmac_string.assert_has_calls(
        [
            call.set(expected_xmove),
            call.set(expected_ymove),
        ]
    )


@patch("mx_bluesky.I24.serial.fixed_target.i24ssx_moveonclick.cv")
@patch("mx_bluesky.I24.serial.fixed_target.i24ssx_moveonclick.get_beam_centre")
def test_update_ui_uses_correct_beam_centre_for_ellipse(fake_beam_pos, fake_cv):
    mock_frame = MagicMock()
    fake_beam_pos.side_effect = [(15, 10)]
    update_ui(mock_frame)
    fake_cv.ellipse.assert_called_once()
    fake_cv.ellipse.assert_has_calls(
        [call(ANY, (15, 10), (12, 8), 0.0, 0.0, 360, (0, 255, 255), thickness=2)]
    )
