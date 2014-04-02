#!/bin/bash
# 2014/4/2
# System Integration Test script for NLAN

python nlan-master.py --scp
python nlan-master.py --scpmod
python nlan-master.py init.run 
python nlan-master.py dvsdvr.yaml 
python nlan-ssh.py openwrt1 --raw 'ip netns exec ns1 ping -c 3 10.0.3.103'
python nlan-ssh.py openwrt3 --raw 'ip netns exec ns3 ping -c 3 10.0.1.101'
python nlan-ssh.py openwrt2 --raw 'ip netns exec ns1 ping -c 3 192.168.100.1'

