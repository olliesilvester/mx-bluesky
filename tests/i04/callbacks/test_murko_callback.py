import json
import pickle
from unittest.mock import MagicMock

import numpy as np
import pytest
from event_model import Event

from mx_bluesky.i04.callbacks.murko_callback import MurkoCallback

test_oav_data = np.array([[1, 2], [3, 4]])
test_smargon_data = 90


def event_template(data_key, data_value) -> Event:
    return {
        "descriptor": "bd45c2e5-2b85-4280-95d7-a9a15800a78b",
        "time": 1666604299.828203,
        "data": {data_key: data_value},
        "timestamps": {data_key: 1666604299.8220396},
        "seq_num": 1,
        "uid": "29033ecf-e052-43dd-98af-c7cdd62e8173",
        "filled": {},
    }


test_oav_event = event_template("oav-array_data", test_oav_data)
test_smargon_event = event_template("smargon-omega", test_smargon_data)
test_uuid = "uuid"

test_start_document = {
    "uid": test_uuid,
    "zoom_percentage": 80,
    "microns_per_x_pixel": 1.2,
    "microns_per_y_pixel": 2.5,
    "beam_centre_i": 158,
    "beam_centre_j": 452,
    "sample_id": 12345,
    "initial_omega": 60,
}


@pytest.fixture
def murko_callback() -> MurkoCallback:
    callback = MurkoCallback()
    callback.redis_client = MagicMock()
    return callback


@pytest.fixture
def murko_with_mock_call(murko_callback) -> MurkoCallback:
    murko_callback.call_murko = MagicMock()
    return murko_callback


def test_when_oav_data_arrives_before_smargon_data_then_murko_called_with_initial_omega_position(
    murko_with_mock_call: MurkoCallback,
):
    murko_with_mock_call.start({"initial_omega": 80})  # type: ignore
    murko_with_mock_call.event(test_oav_event)
    murko_with_mock_call.call_murko.assert_called_once_with(test_oav_data, 80)


def test_when_smargon_data_arrives_then_murko_not_called(
    murko_with_mock_call: MurkoCallback,
):
    murko_with_mock_call.event(test_smargon_event)
    murko_with_mock_call.call_murko.assert_not_called()


def test_when_smargon_data_arrives_before_oav_data_then_murko_called_with_smargon_data(
    murko_with_mock_call: MurkoCallback,
):
    murko_with_mock_call.event(test_smargon_event)
    murko_with_mock_call.event(test_oav_event)
    murko_with_mock_call.call_murko.assert_called_once_with(
        test_oav_data, test_smargon_data
    )


def test_when_murko_called_with_event_data_then_meta_data_put_in_redis(
    murko_callback: MurkoCallback,
):
    murko_callback.start(test_start_document)  # type: ignore
    murko_callback.event(test_smargon_event)
    murko_callback.event(test_oav_event)

    expected_metadata = {
        "uuid": test_uuid,
        "zoom_percentage": 80,
        "microns_per_x_pixel": 1.2,
        "microns_per_y_pixel": 2.5,
        "beam_centre_i": 158,
        "beam_centre_j": 452,
        "sample_id": 12345,
        "omega_angle": test_smargon_data,
    }

    murko_callback.redis_client.hset.assert_any_call(
        "test-metadata", test_uuid, json.dumps(expected_metadata)
    )
    murko_callback.redis_client.publish.assert_called_once_with(
        "murko", json.dumps(expected_metadata)
    )


def test_when_murko_called_with_event_data_then_image_data_put_into_redis(
    murko_callback: MurkoCallback,
):
    murko_callback.start(test_start_document)  # type: ignore
    murko_callback.event(test_smargon_event)
    murko_callback.event(test_oav_event)

    murko_callback.redis_client.hset.assert_any_call(
        "test-image", test_uuid, pickle.dumps(test_oav_data)
    )
