from __future__ import annotations

from collections import namedtuple

import bluesky.plan_stubs as bps
from bluesky import RunEngine

from .smaract import SmarAct

Point3D = namedtuple("Point3D", ("x", "y", "z"))


def move_xz_motors(smaract_motors: SmarAct, pos):
    yield from bps.mv()


def move_omega(smaract_motors: SmarAct):
    yield from bps.mv(smaract_motors.omega, 45)


def exercise_plan():
    pass


def main():
    RE = RunEngine()
    RE(exercise_plan())


main()
