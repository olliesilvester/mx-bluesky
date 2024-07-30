from typing import Dict, Optional

from bluesky.callbacks import CallbackBase
from event_model.documents import Event, EventDescriptor, RunStart


class MurkoCallback(CallbackBase):
    def __init__(self):
        self.descriptors: Dict[str, EventDescriptor] = {}

    def start(self, doc: RunStart) -> Optional[RunStart]:
        self.run_uid = doc.get("uid")
        self.microns_per_x_pixel = doc.get("microns_per_x_pixel")
        self.microns_per_y_pixel = doc.get("microns_per_y_pixel")
        self.beam_centre_i = doc.get("beam_centre_i")
        self.beam_centre_j = doc.get("beam_centre_j")

    def event(self, doc: Event) -> Event:
        print(doc)
        return doc
