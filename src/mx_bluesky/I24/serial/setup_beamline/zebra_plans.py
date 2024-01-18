import logging

import bluesky.plan_stubs as bps
from dodal.devices.zebra import (
    AND3,
    AND4,
    PC_ARM_SOURCE_SOFT,
    PC_GATE_SOURCE_TIME,
    PC_PULSE_SOURCE_EXTERNAL,
    PULSE1,
    ArmDemand,
    Zebra,
)

# Additional sources
SOFT_IN2 = 61
PULSE2 = 53

logger = logging.getLogger("I24ssx.setup_zebra")


def arm_zebra(zebra: Zebra):
    yield from bps.abs_set(zebra.pc.arm, ArmDemand.ARM, wait=True)


def disarm_zebra(zebra: Zebra):
    yield from bps.abs_set(zebra.pc.arm, ArmDemand.DISARM, wait=True)


def setup_zebra_for_quickshot_plan(
    zebra: Zebra,
    gate_start: float,
    gate_width: float,
    group: str = "setup_zebra_for_quickshot",
    wait: bool = False,
):
    """Set up the zebra for a static extruder experiment.

    Args:
        gate_start (float): _description_
        gate_width (float): _description_
        group (str): _description_
        wait (bool): _description_
    """
    logger.info("Setup ZEBRA for quickshot collection.")
    yield from bps.abs_set(zebra.pc.arm_source, PC_ARM_SOURCE_SOFT, group=group)
    yield from bps.abs_set(zebra.pc.gate_source, PC_GATE_SOURCE_TIME, group=group)
    yield from bps.abs_set(zebra.pc.pulse_source, PC_PULSE_SOURCE_EXTERNAL, group=group)

    logger.info(f"Gate start set to {gate_start}, with width {gate_width}.")
    yield from bps.abs_set(zebra.pc.gate_start, gate_start, group=group)
    yield from bps.abs_set(zebra.pc.gate_width, gate_width, group=group)

    # TODO Ask why this is repeated twice.
    yield from bps.abs_set(zebra.pc.gate_input, SOFT_IN2, group=group)
    # yield from bps.sleep(0.1)

    if wait:
        yield from bps.wait(group)


def setup_zebra_for_extruder_with_pump_probe_plan(
    zebra: Zebra,
    det_type: str,
    gate_start: float,
    gate_width: float,
    gate_step: float,
    num_gates: int,
    pulse1_delay: float,
    pulse1_width: float,
    pulse2_delay: float,
    pulse2_width: float,
    group: str = "setup_zebra_for_extruder_pp",
):
    logger.info("Setup ZEBRA for pump probe extruder collection.")
    # SOFT_IN:B0 disabled
    yield from bps.abs_set(zebra.inputs.soft_in_1, 0, group=group)

    # Set gate to "Time" and pulse source to "External"
    yield from bps.abs_set(zebra.pc.gate_source, PC_GATE_SOURCE_TIME, group=group)
    yield from bps.abs_set(zebra.pc.pulse_source, PC_PULSE_SOURCE_EXTERNAL, group=group)

    # Logic gates
    yield from bps.abs_set(zebra.logic_gates.and_gate_3.source_1, SOFT_IN2, group=group)
    yield from bps.abs_set(zebra.logic_gates.and_gate_3.source_2, PULSE1, group=group)
    yield from bps.abs_set(zebra.logic_gates.and_gate_4.source_1, SOFT_IN2, group=group)
    yield from bps.abs_set(zebra.logic_gates.and_gate_4.source_2, PULSE2, group=group)

    # Set TTL out depending on detector type
    if det_type == "eiger":
        yield from bps.abs_set(zebra.output.out_1, AND4, group=group)
        yield from bps.abs_set(zebra.output.out_2, AND3, group=group)
    if det_type == "pilatus":
        yield from bps.abs_set(zebra.output.out_1, AND3, group=group)
        yield from bps.abs_set(zebra.output.out_2, AND4, group=group)

    yield from bps.abs_set(zebra.pc.gate_input, SOFT_IN2, group=group)
    logger.info(f"Gate start set to {gate_start}, with width {gate_width}.")
    yield from bps.abs_set(zebra.pc.gate_start, gate_start, group=group)
    yield from bps.abs_set(zebra.pc.gate_width, gate_width, group=group)
    # TODO ADD PC_GATE_STEP to dodal
