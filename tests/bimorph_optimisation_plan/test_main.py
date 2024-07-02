import json

import pytest
from bimorph_optimisation_plan.__main__ import run_plan


def test_run_plan():
    with open("./tests/test_config.json") as file:
        config_dict = json.load(file)

    run_plan(config_dict)
