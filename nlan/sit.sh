#!/bin/bash
# 2014/4/2
# 2014/4/23
# System Integration Test script for NLAN

export PATH=$PATH:$(pwd)

do_sit () {

    ### SCP NLAN AGENT AND MODULE ###
    nlan.py --scpmod

    if [ $? -gt 0 ]; then
            return 1
    fi

    ### CAUTION: THIS COMMAND DELETE /opt/nlan at all the routers ###
    nlan.py --raw 'rm -rf /opt/nlan'

    ### SCP NLAN AGENT AND MODULE ###
    nlan.py --scpmod

    ### NLAN INITIALIZATION  ###
    #nlan.py init.run
    #nlan.py init.run --info
    nlan.py init.run $1 

    ### NLAN dvsdvr service deployment ###
    #nlan.py dvsdvr.yaml
    #nlan.py dvsdvr.yaml --info
    nlan.py dvsdvr.yaml $1 

    ### CREATE PSEUDO-GLOBAL IP NETWORK ###
    vglobalip.sh

    ### PING TEST ###
    ping.sh

    ### REBOOT ALL THE ROUTERS ###
    nlan.py system.reboot

    ### WAIT UNTIL ALL THE ROUTERS HAVE BEEN REBOOTED ###
    echo ""
    nlan.py -w -50
    echo ""
    nlan.py -w 100

    if [ $? -gt 0 ]; then
            return 1
    fi

    ### CREATE PESUDO-GLOBAL IP NETWORK ###
    vglobalip.sh

    ### PING TEST ###
    ping.sh

    return 0

}

echo "do_sit"
do_sit > ../doc/sit_log.txt
if [ $? -gt 0 ]; then
    echo "FAIL"
    exit 1
else
    echo "SUCCESS"
fi

echo "do_sit --info"
do_sit --info > ../doc/sit_info_log.txt
if [ $? -gt 0 ]; then
    echo "FAIL"
    exit 1
else
    echo "SUCCESS"
fi

echo "do_sit --debug"
do_sit --debug > ../doc/sit_debug_log.txt
if [ $? -gt 0 ]; then
    echo "FAIL"
    exit 1
else
    echo "SUCCESS"
    exit 0
fi

