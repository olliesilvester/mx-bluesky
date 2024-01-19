from dodal.devices.zebra import (
    AND3,
    AND4,
    DISCONNECT,
    PC_GATE_SOURCE_POSITION,
    PC_PULSE_SOURCE_POSITION,
    SOFT_IN2,
    Zebra,
)

from mx_bluesky.I24.serial.setup_beamline.setup_zebra_plans import (
    arm_zebra,
    disarm_zebra,
    setup_zebra_for_extruder_with_pump_probe_plan,
    setup_zebra_for_quickshot_plan,
    zebra_return_to_normal_plan,
)


def test_arm_and_disarm_zebra(zebra: Zebra, RE):
    zebra.pc.arm.TIMEOUT = 0.5

    RE(arm_zebra(zebra))
    assert zebra.pc.is_armed()

    RE(disarm_zebra(zebra))
    assert not zebra.pc.is_armed()


def test_setup_zebra_for_quickshot(zebra: Zebra, RE):
    RE(
        setup_zebra_for_quickshot_plan(
            zebra, gate_start=1.0, gate_width=0.01, wait=True
        )
    )
    assert zebra.pc.arm_source.get() == "Soft"
    assert zebra.pc.gate_start.get() == 1.0
    assert zebra.pc.gate_input.get() == SOFT_IN2


def test_setup_zebra_for_extruder_pp_collection(zebra: Zebra, RE):
    inputs_list = (1.0, 0.1, 0.1, 10, 0.0, 0.001, 0.05, 0.02)
    # With eiger
    RE(
        setup_zebra_for_extruder_with_pump_probe_plan(
            zebra, "eiger", *inputs_list, wait=True
        )
    )
    assert zebra.output.out_1.get() == AND4
    assert zebra.output.out_2.get() == AND3

    assert zebra.inputs.soft_in_1.get() == DISCONNECT
    assert zebra.logic_gates.and_gate_3.source_1.get() == SOFT_IN2
    assert zebra.pc.num_gates.get() == 10

    # With pilatus
    RE(
        setup_zebra_for_extruder_with_pump_probe_plan(
            zebra, "pilatus", *inputs_list, wait=True
        )
    )
    assert zebra.output.out_1.get() == AND3

    assert zebra.pc.gate_start.get() == 1.0
    assert zebra.output.pulse_1_delay.get() == 0.0
    assert zebra.output.pulse_2_delay.get() == 0.05


def test_zebra_return_to_normal(zebra: Zebra, RE):
    RE(zebra_return_to_normal_plan(zebra, wait=True))
    assert not zebra.pc.is_armed()
    assert (
        zebra.pc.gate_source.get() == PC_GATE_SOURCE_POSITION
        and zebra.pc.pulse_source.get() == PC_PULSE_SOURCE_POSITION
    )
    assert zebra.pc.gate_trigger.get() == "Enc2"
    assert zebra.pc.gate_start.get() == 0

    assert zebra.output.out_3.get() == DISCONNECT
    assert zebra.output.pulse_1_input.get() == DISCONNECT
