import json
from argparse import ArgumentParser

from bluesky import RunEngine

from bimorph_optimisation_plan import data_saver, device_instantiator
from bimorph_optimisation_plan.pencil_beam_scan_2d_slit_plan import (
    SlitDimension,
    pencil_beam_scan_2d_slit,
)

from . import __version__

__all__ = ["main"]


def main(args=None):
    parser = ArgumentParser()
    parser.add_argument("config_filepath", type=str, nargs=1, help="Filepath to configuration json")
    parser.add_argument("-v", "--version", action="version", version=__version__)
    args = parser.parse_args(args)

    with open(args.config_filepath[0]) as file:
        config_dict = json.load(file)

    run_plan(config_dict)


def run_plan(config_dict):
    RE = RunEngine({})

    bimorph = device_instantiator.get_bimorph(
        config_dict.get("bimorph_type"),
        config_dict.get("bimorph_prefix"),
        config_dict.get("bimorph_name")
    )

    slit = device_instantiator.get_slit(
        config_dict.get("slit_type"),
        config_dict.get("slit_prefix"),
        config_dict.get("slit_name")
    )

    centroid_device = device_instantiator.get_centroid_device(
        config_dict.get("centroid_device_prefix"), config_dict.get("centroid_device_name"), config_dict.get("values_to_average")
    )

    filename = data_saver.generate_filename(
        config_dict.get("file_prefix"),
        config_dict.get("file_timestamp_format")
    )

    data_list, aggregate_docs = data_saver.define_data_aggregator(
        config_dict.get("output_file_directory"), filename
    )

    print("Starting run...")

    RE(
        pencil_beam_scan_2d_slit(
            bimorph,
            slit,
            centroid_device,
            config_dict.get("voltage_increment"),
            SlitDimension[config_dict.get("active_dimension")],
            config_dict.get("active_slit_center_start"),
            config_dict.get("active_slit_center_end"),
            config_dict.get("active_slit_size"),
            config_dict.get("inactive_slit_center"),
            config_dict.get("inactive_slit_size"),
            config_dict.get("number_of_slit_positions"),
            config_dict.get("bimorph_settle_time"),
            config_dict.get("initial_voltage_list"),
        ),
        aggregate_docs,
    )


# test with: python -m bimorph_optimisation_plan
if __name__ == "__main__":
    main()
