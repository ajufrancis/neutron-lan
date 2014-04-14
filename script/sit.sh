#!/bin/bash
# 2014/4/2
# System Integration Test script for NLAN

python nlan-master.py --scp
python nlan-master.py --scpmod
python nlan-master.py init.run 
python nlan-master.py dvsdvr.yaml 
./vglobalip.sh
./ping.sh

