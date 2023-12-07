from unittest.mock import ANY, MagicMock, call, patch

import cv2 as cv
import pytest

from mx_bluesky.I24.serial.fixed_target.i24ssx_moveonclick import (
    onMouse,
    update_ui,
)


@pytest.mark.parametrize(
    "beam_position, expected_xmove, expected_ymove",
    [
        ((15, 10), -90, -60),
        ((100, 150), -600, -900),
        ((475, 309), -2850, -1854),
        ((638, 392), -3828, -2352),
    ],
)
@patch("mx_bluesky.I24.serial.fixed_target.i24ssx_moveonclick.i24.pmac")
@patch("mx_bluesky.I24.serial.fixed_target.i24ssx_moveonclick.get_beam_centre")
def test_onMouse_gets_beam_position_and_sends_correct_str(
    fake_get_beam_pos,
    fake_pmac,
    beam_position,
    expected_xmove,
    expected_ymove,
):
    fake_get_beam_pos.side_effect = [beam_position]
    fake_pmac.x = MagicMock()
    fake_pmac.y = MagicMock()
    onMouse(cv.EVENT_LBUTTONUP, 0, 0, "", param=fake_pmac)
    fake_pmac.x.assert_has_calls([call.move(expected_xmove)])
    fake_pmac.y.assert_has_calls([call.move(expected_ymove)])


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
