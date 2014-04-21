#!/bin/bash
# 2014/4/2
# System Integration Test script for NLAN

export PATH=$PATH:$(pwd)

### SCP NLAN AGENT AND MODULE ###
nlan.py --scpmod

### CAUTION: THIS COMMAND DELETE /opt/nlan at all the routers ###
nlan.py --raw 'rm -rf /opt/nlan'

### SCP NLAN AGENT AND MODULE ###
nlan.py --scpmod

### NLAN INITIALIZATION  ###
#nlan.py init.run
#nlan.py init.run --info
nlan.py init.run --debug

### NLAN dvsdvr service deployment ###
#nlan.py dvsdvr.yaml
#nlan.py dvsdvr.yaml --info
nlan.py dvsdvr.yaml --debug

### CREATE PSEUDO-GLOBAL IP NETWORK ###
vglobalip.sh

### PING TEST ###
ping.sh

### REBOOT ALL THE ROUTERS ###
nlan.py system.reboot
echo "Make sure all the systems have rebooted!"
echo -n "Enter to proceed the test: "
read ENTER
echo ""

### CREATE PESUDO-GLOBAL IP NETWORK ###
vglobalip.sh

### PING TEST ###
ping.sh

