import logging

import bluesky.plan_stubs as bps
from dodal.devices.zebra import (
    AND3,
    AND4,
    DISCONNECT,
    IN1_TTL,
    IN3_TTL,
    OR1,
    PC_ARM,
    PC_ARM_SOURCE_SOFT,
    PC_GATE,
    PC_GATE_SOURCE_EXTERNAL,
    PC_GATE_SOURCE_POSITION,
    PC_GATE_SOURCE_TIME,
    PC_PULSE,
    PC_PULSE_SOURCE_EXTERNAL,
    PC_PULSE_SOURCE_POSITION,
    PC_PULSE_SOURCE_TIME,
    PULSE1,
    PULSE2,
    SOFT_IN2,
    SOFT_IN3,
    ArmDemand,
    I24Axes,
    RotationDirection,
    Zebra,
)

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
    yield from bps.sleep(0.1)

    if wait:
        yield from bps.wait(group)
    logger.info("Finished setting up zebra.")


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
    wait: bool = False,
):
    logger.info("Setup ZEBRA for pump probe extruder collection.")
    # SOFT_IN:B0 disabled
    yield from bps.abs_set(zebra.inputs.soft_in_1, DISCONNECT, group=group)

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
    yield from bps.abs_set(zebra.pc.gate_step, gate_step, group=group)
    # Number of gates is the same as the number of images
    yield from bps.abs_set(zebra.pc.num_gates, num_gates, group=group)

    # Settingd for extruder pump probe:
    # PULSE1_DLY is the start (0 usually), PULSE1_WID is the laser dwell set on edm
    # PULSE2_DLY is the laser delay set on edm, PULSE2_WID is the exposure time
    logger.info(
        f"Pulse1 starting at {pulse1_delay} with width set to laser dwell {pulse1_width}."
    )
    yield from bps.abs_set(zebra.output.pulse_1.pulse_inp, PC_GATE, group=group)
    yield from bps.abs_set(zebra.output.pulse_1.pulse_dly, pulse1_delay, group=group)
    yield from bps.abs_set(zebra.output.pulse_1.pulse_wid, pulse1_width, group=group)
    logger.info(
        f"""
        Pulse2 starting at laser delay {pulse2_delay} with width set to \
        exposure time {pulse2_delay}
        """
    )
    yield from bps.abs_set(zebra.output.pulse_2.pulse_inp, PC_GATE, group=group)
    yield from bps.abs_set(zebra.output.pulse_2.pulse_dly, pulse2_delay, group=group)
    yield from bps.abs_set(zebra.output.pulse_2.pulse_wid, pulse2_width, group=group)

    if wait:
        yield from bps.wait(group)
    logger.info("Finished setting up zebra.")


def setup_zebra_for_fastchip_plan(
    zebra: Zebra,
    det_type: str,
    num_gates: int,
    num_exposures: int,
    exposure_time: float,
    group: str = "setup_zebra_for_fastchip",
    wait: bool = False,
):
    logger.info("Setup ZEBRA for a fixed target collection.")
    # SOFT_IN:B0 disabled
    yield from bps.abs_set(zebra.inputs.soft_in_1, DISCONNECT, group=group)
    yield from bps.abs_set(zebra.pc.gate_source, PC_GATE_SOURCE_EXTERNAL, group=group)
    yield from bps.abs_set(zebra.pc.pulse_source, PC_PULSE_SOURCE_TIME, group=group)

    # Logic Gates
    yield from bps.abs_set(zebra.logic_gates.and_gate_3.source_1, SOFT_IN2, group=group)
    yield from bps.abs_set(zebra.logic_gates.and_gate_3.source_2, PC_PULSE, group=group)

    yield from bps.abs_set(zebra.pc.gate_input, IN3_TTL, group=group)

    # Set TTL out depending on detector type
    # And calculate some of the other settings
    if det_type == "eiger":
        yield from bps.abs_set(zebra.output.out_1, AND3, group=group)
    if det_type == "pilatus":
        yield from bps.abs_set(zebra.output.out_2, AND3, group=group)

    # Sawtooth - needs a small drop to make it work for eiger
    pulse_width = exposure_time - 0.0001 if det_type == "eiger" else exposure_time / 2

    # 100us buffer needed to avoid missing some of the triggers
    exptime_buffer = exposure_time + 0.0001

    # Number of gates is the number of windows collected
    yield from bps.abs_set(zebra.pc.num_gates, num_gates, group=group)

    yield from bps.abs_set(zebra.pc.pulse_start, 0, group=group)
    yield from bps.abs_set(zebra.pc.pulse_step, exptime_buffer, group=group)
    yield from bps.abs_set(zebra.pc.pulse_width, pulse_width, group=group)
    yield from bps.abs_set(zebra.pc.pulse_max, num_exposures, group=group)

    if wait:
        yield from bps.wait(group)
    logger.info("Finished setting up zebra.")


def zebra_return_to_normal_plan(
    zebra: Zebra, group: str = "zebra-return-to-normal", wait: bool = False
):
    """A plan to reset the Zebra at the end of a collection."""
    if zebra.pc.is_armed():
        logger.info("Zebra is still armed. Disarming before proceeding.")
        yield from disarm_zebra(zebra)
        yield from bps.sleep(0.1)

    # Reset PC_GATE and PC_SOURCE to "Position"
    yield from bps.abs_set(zebra.pc.gate_source, PC_GATE_SOURCE_POSITION, group=group)
    yield from bps.abs_set(zebra.pc.pulse_source, PC_PULSE_SOURCE_POSITION, group=group)

    yield from bps.abs_set(zebra.pc.gate_input, SOFT_IN3, group=group)
    yield from bps.abs_set(zebra.pc.num_gates, 1, group=group)
    yield from bps.abs_set(zebra.pc.pulse_input, DISCONNECT, group=group)

    # Logic Gates
    yield from bps.abs_set(zebra.logic_gates.and_gate_3.source_1, PC_ARM, group=group)
    yield from bps.abs_set(zebra.logic_gates.and_gate_3.source_2, IN1_TTL, group=group)

    # TTL out
    yield from bps.abs_set(zebra.output.out_2, PC_GATE, group=group)
    yield from bps.abs_set(zebra.output.out_3, DISCONNECT, group=group)
    yield from bps.abs_set(zebra.output.out_4, OR1, group=group)

    # Reset rotation axis and direction to "omega" and positive
    yield from bps.abs_set(zebra.pc.gate_trigger, I24Axes.OMEGA.value, group=group)
    yield from bps.abs_set(zebra.pc.dir, RotationDirection.POSITIVE, group=group)

    #
    yield from bps.abs_set(zebra.pc.gate_start, 0, group=group)
    yield from bps.abs_set(zebra.pc.pulse_width, 0, group=group)
    yield from bps.abs_set(zebra.pc.pulse_step, 0, group=group)

    yield from bps.abs_set(zebra.output.pulse_1.pulse_inp, DISCONNECT, group=group)
    yield from bps.abs_set(zebra.output.pulse_2.pulse_inp, DISCONNECT, group=group)

    if wait:
        yield from bps.wait(group)
    logger.info("Zebra settings back to normal.")
