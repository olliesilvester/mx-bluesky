import copy
import json
import pickle
from typing import Dict, Optional

import numpy as np
import redis
from bluesky.callbacks import CallbackBase
from dodal.log import LOGGER
from event_model.documents import Event, EventDescriptor, RunStart


class MurkoCallback(CallbackBase):
    def __init__(self):
        self.descriptors: Dict[str, EventDescriptor] = {}
        self.redis_client = redis.StrictRedis(host="i04-control.diamond.ac.uk", db=7)

    def start(self, doc: RunStart) -> Optional[RunStart]:
        self.uuid = doc.get("uid")
        self.murko_metadata = {
            "uuid": self.uuid,
            "zoom_percentage": doc.get("zoom_percentage"),
            "microns_per_x_pixel": doc.get("microns_per_x_pixel"),
            "microns_per_y_pixel": doc.get("microns_per_y_pixel"),
            "beam_centre_i": doc.get("beam_centre_i"),
            "beam_centre_j": doc.get("beam_centre_j"),
            "sample_id": doc.get("sample_id"),
        }
        self.last_omega_position = doc.get("initial_omega")

    def event(self, doc: Event) -> Event:
        if latest_omega := doc["data"].get("smargon-omega"):
            self.last_omega_position = latest_omega
        elif (oav_image := doc["data"].get("oav-array_data")) is not None:
            self.call_murko(oav_image, self.last_omega_position)
        return doc

    def call_murko(self, image: np.ndarray, omega: float):
        metadata = copy.deepcopy(self.murko_metadata)
        metadata["omega_angle"] = omega

        # Send metadata and image to REDIS
        self.redis_client.hset("test-metadata", self.uuid, json.dumps(metadata))
        self.redis_client.hset("test-image", self.uuid, pickle.dumps(image))
        self.redis_client.publish("murko", json.dumps(metadata))
        LOGGER.info("OAV frame sent to redis")
