"""
Zebra setup plans for extruder and fastchip serial collections.

For clarification on the Zebra setup in either use case, please see
https://confluence.diamond.ac.uk/display/MXTech/Zebra+settings+I24
"""

import logging
from typing import Optional

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
    FastShutterAction,
    I24Axes,
    RotationDirection,
    Zebra,
)

# Detector specific outs
TTL_EIGER = 1
TTL_PILATUS = 2

SHUTTER_MODE = {
    "manual": DISCONNECT,
    "auto": IN1_TTL,
}

logger = logging.getLogger("I24ssx.setup_zebra")


def get_zebra_settings_for_extruder(
    plan_name: str,
    exp_time: float,
    num_imgs: int,
    pump_exp: Optional[float] = None,
    pump_delay: Optional[float] = None,
):
    """Calculates and returns gate start, width and step for extruder collections, \
    depending on the plan being run.

    Gate start is hard coded to 1.0 in all cases.
    For a quickshot plan, only the gate width is needed and it is calculated from \
    exposure time*number of images plus a 0.5 buffer.
    For a pump probe plan, the gate width is calculated by adding the exposure time, \
    pump exposure and pump delay. From this value, the gate step is obtained by adding \
    a 0.01 buffer to the width. The value of this buffer is empirically determined.
    """
    gate_start = 1.0
    if plan_name == "quickshot":
        gate_width = exp_time * num_imgs + 0.5
        return gate_start, gate_width, None
    probepumpbuffer = 0.01
    gate_width = pump_exp + pump_delay + exp_time
    gate_step = gate_width + probepumpbuffer
    return gate_start, gate_width, gate_step


def arm_zebra(zebra: Zebra):
    yield from bps.abs_set(zebra.pc.arm, ArmDemand.ARM, wait=True)


def disarm_zebra(zebra: Zebra):
    yield from bps.abs_set(zebra.pc.arm, ArmDemand.DISARM, wait=True)


def open_fast_shutter(zebra: Zebra):
    yield from bps.abs_set(zebra.inputs.soft_in_2, FastShutterAction.OPEN, wait=True)
    logger.info("Fast shutter open.")


def close_fast_shutter(zebra: Zebra):
    yield from bps.abs_set(zebra.inputs.soft_in_2, FastShutterAction.CLOSE, wait=True)
    logger.info("Fast shutter closed.")


def set_shutter_mode(zebra: Zebra, mode: str):
    # SOFT_IN:B0 has to be disabled for manual mode
    yield from bps.abs_set(zebra.inputs.soft_in_1, SHUTTER_MODE[mode], wait=True)
    logger.info(f"Shutter mode set to {mode}.")


def setup_pc_sources(
    zebra: Zebra, gate_source: int, pulse_source: int, group: str = "pc_sources"
):
    yield from bps.abs_set(zebra.pc.gate_source, gate_source, group=group)
    yield from bps.abs_set(zebra.pc.pulse_source, pulse_source, group=group)
    yield from bps.wait(group)


def setup_zebra_for_quickshot_plan(
    zebra: Zebra,
    exp_time: float,
    num_images: int,
    group: str = "setup_zebra_for_quickshot",
    wait: bool = False,
):
    """Set up the zebra for a static extruder experiment.

    Gate source set to 'External' and Pulse source set to 'Time'.

    Args:
        zebra (Zebra): The zebra ophyd device.
        exp_time (float): Collection exposure time, in s.
        num_images (float): Number of images to be collected.
    """
    logger.info("Setup ZEBRA for quickshot collection.")
    yield from bps.abs_set(zebra.pc.arm_source, PC_ARM_SOURCE_SOFT, group=group)
    yield from setup_pc_sources(zebra, PC_GATE_SOURCE_TIME, PC_PULSE_SOURCE_EXTERNAL)

    gate_start, gate_width, _ = get_zebra_settings_for_extruder(
        "quickshot", exp_time, num_images
    )
    logger.info(f"Gate start set to {gate_start}, with width {gate_width}.")
    yield from bps.abs_set(zebra.pc.gate_start, gate_start, group=group)
    yield from bps.abs_set(zebra.pc.gate_width, gate_width, group=group)

    yield from bps.abs_set(zebra.pc.gate_input, SOFT_IN2, group=group)
    yield from bps.sleep(0.1)

    if wait:
        yield from bps.wait(group)
    logger.info("Finished setting up zebra.")


def set_logic_gates_for_porto_triggering(
    zebra: Zebra, group: str = "porto_logic_gates"
):
    yield from bps.abs_set(zebra.logic_gates.and_gate_3.source_1, SOFT_IN2, group=group)
    yield from bps.abs_set(zebra.logic_gates.and_gate_3.source_2, PULSE1, group=group)
    yield from bps.abs_set(zebra.logic_gates.and_gate_4.source_1, SOFT_IN2, group=group)
    yield from bps.abs_set(zebra.logic_gates.and_gate_4.source_2, PULSE2, group=group)
    yield from bps.wait(group=group)


def setup_zebra_for_extruder_with_pump_probe_plan(
    zebra: Zebra,
    det_type: str,
    exp_time: float,
    num_images: int,
    pump_exp: float,
    pump_delay: float,
    pulse1_delay: float = 0.0,
    group: str = "setup_zebra_for_extruder_pp",
    wait: bool = False,
):
    """Zebra setup for extruder pump probe experiment with PORTO.

    For this use case, both the laser and detector set up is taken care of by the Zebra.
    WARNING. This means that some hardware changes have been made.
    Because all four of the zebra ttl outputs are in use in this mode, when the \
    detector in use is the Eiger, the Pilatus cable is repurposed to trigger the light \
    source, and viceversa.

    The data collection output is OUT1_TTL for Eiger and OUT2_TTL for Pilatus and \
    should be set to AND3.

    Position compare settings:
        - The gate input is on SOFT_IN2.
        - The number of gates should be equal to the number of images to collect.
        - Gate source set to 'Time' and Pulse source set to 'External'.

    Pulse output settings:
        - Pulse1 is the laser control on the Zebra. It is set with a 0.0 delay and a \
            width equal to the requested laser dwell.
        - Pulse2 is the detector control. It is set with a delay equal to the laser \
            delay and a width equal to the exposure time.

    Args:
        zebra (Zebra): The zebra ophyd device.
        det_type (str): Detector in use, current choices are Eiger or Pilatus.
        exp_time (float): Collection exposure time, in s.
        num_images (int): Number of images to be collected.
        pump_exp (float): Laser dwell, in s.
        pump_delay (float): Laser delay, in s.
        pulse1_delay (float, optional): Delay to start pulse1 (the laser control) after \
            gate start. Defaults to 0.0.
    """
    logger.info("Setup ZEBRA for pump probe extruder collection.")

    yield from set_shutter_mode(zebra, "manual")

    # Set gate to "Time" and pulse source to "External"
    yield from setup_pc_sources(zebra, PC_GATE_SOURCE_TIME, PC_PULSE_SOURCE_EXTERNAL)

    # Logic gates
    yield from set_logic_gates_for_porto_triggering(zebra)

    # Set TTL out depending on detector type
    DET_TTL = TTL_EIGER if det_type == "eiger" else TTL_PILATUS
    LASER_TTL = TTL_PILATUS if det_type == "eiger" else TTL_EIGER
    yield from bps.abs_set(zebra.output.out_pvs[DET_TTL], AND4, group=group)
    yield from bps.abs_set(zebra.output.out_pvs[LASER_TTL], AND3, group=group)

    yield from bps.abs_set(zebra.pc.gate_input, SOFT_IN2, group=group)

    gate_start, gate_width, gate_step = get_zebra_settings_for_extruder(
        "pump-probe", exp_time, num_images, pump_exp, pump_delay
    )
    logger.info(
        f"""
        Gate start set to {gate_start}, with calculated width {gate_width}
        and step {gate_step}.
        """
    )
    yield from bps.abs_set(zebra.pc.gate_start, gate_start, group=group)
    yield from bps.abs_set(zebra.pc.gate_width, gate_width, group=group)
    yield from bps.abs_set(zebra.pc.gate_step, gate_step, group=group)
    # Number of gates is the same as the number of images
    yield from bps.abs_set(zebra.pc.num_gates, num_images, group=group)

    # Settings for extruder pump probe:
    # PULSE1_DLY is the start (0 usually), PULSE1_WID is the laser dwell set on edm
    # PULSE2_DLY is the laser delay set on edm, PULSE2_WID is the exposure time
    logger.info(
        f"Pulse1 starting at {pulse1_delay} with width set to laser dwell {pump_exp}."
    )
    yield from bps.abs_set(zebra.output.pulse_1.inp, PC_GATE, group=group)
    yield from bps.abs_set(zebra.output.pulse_1.dly, pulse1_delay, group=group)
    yield from bps.abs_set(zebra.output.pulse_1.wid, pump_exp, group=group)
    logger.info(
        f"""
        Pulse2 starting at laser delay {pump_delay} with width set to \
        exposure time {exp_time}.
        """
    )
    yield from bps.abs_set(zebra.output.pulse_2.inp, PC_GATE, group=group)
    yield from bps.abs_set(zebra.output.pulse_2.dly, pump_delay, group=group)
    yield from bps.abs_set(zebra.output.pulse_2.wid, exp_time, group=group)

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
    """Zebra setup for fixed-target triggering.

    For this use case, the laser set up is taken care of by the geobrick, leaving only \
    the detector side set up to the Zebra.
    The data collection output is OUT1_TTL for Eiger and OUT2_TTL for Pilatus and \
    should be set to AND3.

    Position compare settings:
        - The gate input is on IN3_TTL.
        - The number of gates should be equal to the number of apertures to collect.
        - Gate source set to 'External' and Pulse source set to 'Time'
        - Trigger source set to the exposure time with a 100us buffer in order to \
            avoid missing any triggers.
        - The trigger width is calculated depending on which detector is in use: the \
            Pilatus only needs the trigger rising edge to collect for a set time, while \
            the Eiger will only collect while the signal is high and will stop once \
            a falling edge is detected. For this reason a sawtooth will be set to half \
            the exposure time in the Pilatus case, and to the exposure time minus a \
            small drop (~100um) for the Eiger.

    Args:
        zebra (Zebra): The zebra ophyd device.
        det_type (str): Detector in use, current choices are Eiger or Pilatus.
        num_gates (int): Number of apertures to visit in a chip.
        num_exposures (int): Number of times data is collected in each aperture.
        exposure_time (float): Exposure time for each shot.
    """
    logger.info("Setup ZEBRA for a fixed target collection.")

    yield from set_shutter_mode(zebra, "manual")

    yield from setup_pc_sources(zebra, PC_GATE_SOURCE_EXTERNAL, PC_PULSE_SOURCE_TIME)

    # Logic Gates
    yield from bps.abs_set(zebra.logic_gates.and_gate_3.source_1, SOFT_IN2, group=group)
    yield from bps.abs_set(zebra.logic_gates.and_gate_3.source_2, PC_PULSE, group=group)

    yield from bps.abs_set(zebra.pc.gate_input, IN3_TTL, group=group)

    # Set TTL out depending on detector type
    # And calculate some of the other settings
    if det_type == "eiger":
        yield from bps.abs_set(zebra.output.out_pvs[TTL_EIGER], AND3, group=group)
    if det_type == "pilatus":
        yield from bps.abs_set(zebra.output.out_pvs[TTL_PILATUS], AND3, group=group)

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


def position_compare_off(zebra: Zebra, group: str = "position_compare_off"):
    yield from bps.abs_set(zebra.pc.gate_start, 0, group=group)
    yield from bps.abs_set(zebra.pc.pulse_width, 0, group=group)
    yield from bps.abs_set(zebra.pc.pulse_step, 0, group=group)
    yield from bps.wait(group=group)


def reset_output_panel(zebra: Zebra, group: str = "reset_zebra_outputs"):
    # Reset TTL out
    yield from bps.abs_set(zebra.output.out_2, PC_GATE, group=group)
    yield from bps.abs_set(zebra.output.out_3, DISCONNECT, group=group)
    yield from bps.abs_set(zebra.output.out_4, OR1, group=group)

    yield from bps.abs_set(zebra.output.pulse_1.inp, DISCONNECT, group=group)
    yield from bps.abs_set(zebra.output.pulse_2.inp, DISCONNECT, group=group)

    yield from bps.wait(group=group)


def zebra_return_to_normal_plan(
    zebra: Zebra, group: str = "zebra-return-to-normal", wait: bool = False
):
    """A plan to reset the Zebra settings at the end of a collection.

    This plan should only be run after disarming the Zebra.
    """
    yield from bps.abs_set(zebra.pc.reset, 1, group=group)

    # Reset PC_GATE and PC_SOURCE to "Position"
    yield from setup_pc_sources(
        zebra, PC_GATE_SOURCE_POSITION, PC_PULSE_SOURCE_POSITION
    )

    yield from bps.abs_set(zebra.pc.gate_input, SOFT_IN3, group=group)
    yield from bps.abs_set(zebra.pc.num_gates, 1, group=group)
    yield from bps.abs_set(zebra.pc.pulse_input, DISCONNECT, group=group)

    # Logic Gates
    yield from bps.abs_set(zebra.logic_gates.and_gate_3.source_1, PC_ARM, group=group)
    yield from bps.abs_set(zebra.logic_gates.and_gate_3.source_2, IN1_TTL, group=group)

    # Reset TTL out
    yield from reset_output_panel(zebra)

    # Reset Pos Trigger and direction to rotation axis ("omega") and positive
    yield from bps.abs_set(zebra.pc.gate_trigger, I24Axes.OMEGA.value, group=group)
    yield from bps.abs_set(zebra.pc.dir, RotationDirection.POSITIVE, group=group)

    #
    yield from position_compare_off(zebra)

    if wait:
        yield from bps.wait(group)
    logger.info("Zebra settings back to normal.")


def reset_zebra_when_collection_done_plan(zebra: Zebra):
    """
    End of collection zebra operations: close fast shutter, disarm and reset settings.
    """
    logger.debug("Close the fast shutter.")
    yield from close_fast_shutter(zebra)
    logger.debug("Disarm the zebra.")
    yield from disarm_zebra(zebra)
    yield from zebra_return_to_normal_plan(zebra, wait=True)
