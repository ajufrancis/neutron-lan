#!/bin/bash
# 2014/4/2
# System Integration Test script for NLAN

export PATH=$PATH:$(pwd)

nlan_master.py --scpmod
#nlan_master.py init.run
#nlan_master.py init.run --info
nlan_master.py init.run --debug
#nlan_master.py dvsdvr.yaml
#nlan_master.py dvsdvr.yaml --info
nlan_master.py dvsdvr.yaml --debug

./vglobalip.sh
./ping.sh

