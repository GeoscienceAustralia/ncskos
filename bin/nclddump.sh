#!/bin/bash
# Shell script to invoke nclddump Python script in BASH
# Written by Alex Ip 4/10/2016
# Example invocation: nclddump.sh -hs /home/547/axi547/sst.ltm.1971-2000_skos.nc --skos lang=pl altLabels=True narrower=True broader=True

# Assume script is in bin directory under module directory
export PYTHONPATH=$(dirname $(dirname $(readlink -f "$0"))):$PYTHONPATH
echo $PYTHONPATH

python -m nclddump $@
