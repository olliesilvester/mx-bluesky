import json

def get_plan_arguments(config_path):
    with open(config_path) as file:
        json_dict = json.load(file)
    