from mx_bluesky.I24.serial.setup_beamline import Eiger, Extruder, FixedTarget, Pilatus


def test_eiger():
    eig = Eiger()
    assert eig.image_size_mm == (233.1, 244.65)


def test_pilatus():
    pil = Pilatus()
    assert pil.image_size_mm == (423.636, 434.644)


def test_experiment_types():
    assert Extruder().expt_type.value == "Serial Jet"
    assert FixedTarget().expt_type.value == "Serial Fixed"
