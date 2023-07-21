#!/bin/bash

# Start the edm screen relative to requested serial collection
expt_type=${1:-FT}

echo "Activate python environment before starting edm screen"
source /dls_sw/i24/software/bluesky/mx_bluesky/.venv/bin/activate

shopt -s nocasematch

if [[ $expt_type == "FT" ]] || [[ $expt_type == "fixed-target" ]]
then
    echo "Starting fixed target edm screen."
    edm /dls_sw/i24/software/bluesky/mx_bluesky/src/mx_bluesky/I24/serial/fixed_target/FT-gui-edm/DiamondChipI24-py3v1.edl
elif [[ $expt_type == "EX" ]] || [[ $expt_type == "extruder" ]]
then
    echo "Starting extruder edm screen."
    edm /dls_sw/i24/software/bluesky/mx_bluesky/src/mx_bluesky/I24/serial/extruder/EX-gui-edm/DiamondExtruder-I24-py3v1.edl
else
    echo "No edm found for $expt_type."
fi

echo "Edm screen closed, deactivate python environment"
deactivate
