#!/bin/bash
# Shell script to invoke nclddump Python script in BASH
# Written by Alex Ip 4/10/2016
# Example invocation: nclddump.sh -h /home/547/axi547/sst.ltm.1971-2000_skos.nc --skos lang=pl altLabels=True narrower=True broader=True

export PYTHONPATH=../:%PYTHONPATH%

python -m nclddump $@