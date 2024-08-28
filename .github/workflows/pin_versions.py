#!/usr/bin/env python3
import argparse
import locale
import os
import re
import subprocess
from functools import partial
from sys import stderr, stdout

import requests

PYPROJECT_TOML_PATTERN = re.compile("(.*?\\S)\\s*(@(.*))?$")
PYPROJECT_UNPINNED_PATTERN = re.compile("(.*?\\S)\\s*([<>=]+(.*))?$")
PIP = "pip"


def rename_original(suffix):
    os.rename("pyproject.toml", "pyproject.toml" + suffix)


def normalize(package_name: str):
    # Replace underscore and dots with hyphen, and convert to lower case
    package_name = re.sub(r"[-_.]+", "-", package_name).lower()

    package_name = package_name.replace('"', "")
    package_name = package_name.replace(",", "")

    # Remove square brackets in pip freeze, eg "fastapi[all]"" to "fastapi"
    package_name = re.sub(r"\[.*\]$", "", package_name)
    print(package_name)
    return package_name


# Returns latest version of dodal by looking at most recent tag on github
def _get_dodal_version() -> str:
    url = "https://api.github.com/repos/DiamondLightSource/dodal/tags"
    response = requests.get(url)

    if response.status_code == 200:
        tags = response.json()
        if tags:
            return str(tags[0]["name"])
        else:
            stderr.write("Unable to find latest dodal tag")

    stderr.write("Unable to find dodal on github")
    raise Exception("Error finding the latest dodal version")


def fetch_pin_versions() -> dict[str, str]:
    process = run_pip_freeze()
    if process.returncode == 0:
        output = process.stdout
        lines = output.split("\n")
        pin_versions = {}
        for line in lines:
            kvpair = line.split("==")
            if len(kvpair) != 2:
                # mx_bluesky will appear as '-e git+ssh://git@github.com/DiamondLightSource/mx-bluesky',
                # and same for dodal unless it has manually been pinned beforehand
                if line and not ("dls_dodal" in line or "mx_bluesky" in line):
                    stderr.write(
                        f"Unable to parse {line} - make sure this dependancy isn't pinned to a git hash\n"
                    )
            else:
                pin_versions[normalize(kvpair[0]).strip()] = kvpair[1].strip()

        # Handle dodal separately to save us from having to manually set it
        pin_versions["dls-dodal"] = _get_dodal_version()

        return pin_versions
    else:
        stderr.write(f"pip freeze failed with error code {process.returncode}\n")
        stderr.write(process.stderr)
        exit(1)


def run_pip_freeze():
    process = subprocess.run(
        [PIP, "list --format=freeze"],
        capture_output=True,
        encoding=locale.getpreferredencoding(),
    )
    return process


def process_pyproject_toml(input_fname, output_fname, dependency_processor):
    with open(input_fname) as input_file:
        with open(output_fname, "w") as output_file:
            process_files(input_file, output_file, dependency_processor)


def process_files(input_file, output_file, dependency_processor):
    while line := input_file.readline():
        output_file.write(line)
        if line.startswith("dependencies"):
            break
    while (line := input_file.readline()) and not line.startswith("]"):
        if line.isspace():
            output_file.write(line)
        else:
            dependency_processor(line, output_file)
    output_file.write(line)
    while line := input_file.readline():
        output_file.write(line)


def strip_comment(line: str):
    split = line.rstrip("\n").split("#", 1)
    return split[0], (split[1] if len(split) > 1 else None)


def write_with_comment(comment, text, output_file):
    output_file.write(text)
    if comment:
        output_file.write(" #" + comment)
    output_file.write("\n")


def update_pyproject_toml_line(version_map: dict[str, str], line, output_file):
    stripped_line, comment = strip_comment(line)
    if match := PYPROJECT_UNPINNED_PATTERN.match(stripped_line):
        normalized_name = normalize(match[1].strip())
        if normalized_name not in version_map:
            stderr.write(
                f"Unable to find {normalized_name} in installed python packages\n"
            )
            exit(1)

        write_with_comment(
            comment,
            f'    "{normalized_name} == {version_map[normalized_name]}",',
            output_file,
        )
    else:
        output_file.write(line)


def write_commit_message(pinned_versions: dict[str, str]):
    message = f"Pin dependencies prior to release. Dodal {pinned_versions['dls-dodal']}, nexgen {pinned_versions['nexgen']}"
    stdout.write(message)


def unpin_versions(line, output_file):
    stripped_line, comment = strip_comment(line)
    if match := PYPROJECT_TOML_PATTERN.match(stripped_line):
        if match[3] and match[3].strip().startswith("git+"):
            write_with_comment(comment, match[1] + '",', output_file)
            return

    output_file.write(line)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Pin dependency versions in pyproject.toml"
    )
    parser.add_argument(
        "--unpin",
        help="remove pinned hashes from pyproject.toml prior to pip installing latest",
        action="store_true",
    )
    args = parser.parse_args()

    if args.unpin:
        rename_original(".orig")
        process_pyproject_toml("pyproject.toml.orig", "pyproject.toml", unpin_versions)
    else:
        rename_original(".unpinned")
        installed_versions = fetch_pin_versions()
        process_pyproject_toml(
            "pyproject.toml.unpinned",
            "pyproject.toml",
            partial(update_pyproject_toml_line, installed_versions),
        )
        write_commit_message(installed_versions)
