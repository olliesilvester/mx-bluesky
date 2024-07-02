from datetime import datetime
from typing import Callable

def generate_filename(file_prefix:str = None, file_timestamp_format:str = None) -> str:
    """Generated a filename (without path) for plan output csv

    Args:
        file_prefix (optional): Prefix for filename
        file_timestamp_format (optional): datetime library timestamp format for filename
    
    Returns:
        A string fiename without full path
    """
    filename = ""

    if file_prefix is not None:
        filename += file_prefix
    else:
        filename += "pencilbeam-data-"
    
    if file_timestamp_format is not  None:
        filename += datetime.now().strftime(file_timestamp_format)
    else:
        filename += datetime.now().strftime("%d-%m-%Y-%H-%M")
    
    filename += ".csv"

    return filename


def make_csv(docs: list) -> str:
    """
    Takes a list of RunEngine output docs and converts to CSV format

    Args:
        docs: A list of RunEngine docs
    
    Returms:
        A string of given list's csv equivalent
    """
    csv_dict = {}
    headers = []

    for doc in docs:
        if "run_start" in doc and "data_keys" in doc:
            headers = [header for header in doc["data_keys"]]
            headers.sort()
            for header in headers:
                csv_dict[header] = []

        elif "descriptor" in doc:
            for header in doc["data"]:
                csv_dict[header].append(str(doc["data"][header]))

    csv_str = ",".join(headers) + "\n"

    csv_str += "\n".join(
        [",".join(row) for row in zip(*[csv_dict[header] for header in headers])]
    )

    # return csv_str
    return csv_str


def define_data_aggregator(filepath: str, filename: str) -> tuple[list, Callable]:
    """
    Create a data structure and defines a function to give to Run Engine to save data

    Args:
        filepath: Directory to save file into
        filename: Filename for output csv
    
    Returns:
        A list that aggregates data, a function to give as sub to Run Engine
    """

    data_list = []

    def aggregate_docs(_, doc):
        data_list.append(doc)
        csv = make_csv(data_list)

        with open(filepath + '/' + filename, 'w') as file:
            file.write(csv)
    
    return data_list, aggregate_docs




