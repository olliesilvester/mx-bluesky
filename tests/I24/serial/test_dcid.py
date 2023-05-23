from mx_bluesky.I24.serial.dcid import get_beam_center, get_beamsize, get_resolution
from mx_bluesky.I24.serial.setup_beamline import Eiger, Pilatus


def test_beamsize():
    beam_size = get_beamsize()
    print("Beam size: ", beam_size)
    assert type(beam_size) is tuple


def test_beam_center():
    print("Beam center: ", get_beam_center(Eiger()))


def test_get_resolution():
    distance = 100
    wavelength = 0.649

    eiger_resolution = get_resolution(Eiger(), distance, wavelength)
    pilatus_resolution = get_resolution(Pilatus(), distance, wavelength)

    assert eiger_resolution == 0.78
    assert pilatus_resolution == 0.61
