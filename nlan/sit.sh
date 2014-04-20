#!/bin/bash
# 2014/4/2
# System Integration Test script for NLAN

export PATH=$PATH:$(pwd)

nlan.py --scpmod
nlan.py init.run
#nlan.py init.run --info
#nlan.py init.run --debug
nlan.py dvsdvr.yaml
#nlan.py dvsdvr.yaml --info
#nlan.py dvsdvr.yaml --debug

./vglobalip.sh
./ping.sh

