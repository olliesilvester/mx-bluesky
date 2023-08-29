#!/bin/bash

# Set visit directory for current experiment type from values stored in a file
filename="/dls_sw/i24/etc/ssx_current_visit.txt"

if [[ ! -f "$filename" ]]; then
    echo "The file $filename does not exist. Impossible to set the visit directory."
    exit 1
fi


echo "Reading file: $filename"

visit=$(sed -n '1p' $filename)
expt_type=${1:-FT}

ex_pv=BL24I-EA-IOC-12:GP1
ft_pv=ME14E-MO-IOC-01:GP100

shopt -s nocasematch

if [[ $expt_type == "FT" ]] || [[ $expt_type == "fixed-target" ]]
then
    echo "Setting visit PV for serial fixed-target collection."
    caput  $ft_pv $visit
    echo "Visit set to: $visit."
elif [[ $expt_type == "EX" ]] || [[ $expt_type == "extruder" ]]
then
    echo "Setting visit PV for serial extruder collection."
    caput  $ex_pv $visit
    echo "Visit set to: $visit"
else
    echo -e "Unknown experiment type, visit PV not set. \nValid experiment values: fixed-target, extruder."
    exit 1
fi