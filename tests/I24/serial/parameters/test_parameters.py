from mx_bluesky.I24.serial.parameters.experiment_parameters import GeneralParameters


def test_general_parameters():
    gen = GeneralParameters(
        visit="path/to",
        directory="dir",
        filename="ciao00",
        exp_time=0.1,
        det_type="pilatus",
        det_dist=300.0,
    )

    assert gen.filename.endswith("-")
    assert gen.collection_path == gen.visit / gen.directory
