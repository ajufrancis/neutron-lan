#!/bin/bash
export PATH=$PATH:$(pwd)
nlan.py -t openwrt1 --raw 'echo a b c'
nlan.py -t openwrt1 --raw 'ip netns exec ns1 ping -c 2 10.0.1.102'
nlan.py -t openwrt1 --raw 'ip netns exec ns1 ping -c 2 10.0.1.102'
nlan.py -t openwrt1 --raw 'ip netns exec ns3 ping -c 2 10.0.3.103'
nlan.py -t openwrt3 --raw 'ip netns exec ns3 ping -c 2 10.0.1.101'
nlan.py -t openwrt2 --raw 'ip netns exec ns1 ping -c 2 192.168.100.1'
nlan.py -t openwrt3 --raw 'ip netns exec ns1 ping -c 2 192.168.100.1'
nlan.py -t openwrt2 --raw 'ip netns exec ns3 ping -c 2 192.168.100.1'
nlan.py -t openwrt2 --raw 'ping -c 2 192.168.100.1'
nlan.py -t openwrt3 --raw 'ip netns exec ns3 ping -c 2 10.0.1.102'
nlan.py -t openwrt3 --raw 'ip netns exec ns3 ping -c 2 10.0.1.1'
nlan.py -t openwrt2 --raw 'ip netns exec ns3 ping -c 2 10.0.1.1'
nlan.py -t openwrt2 --raw 'ip netns exec ns1 ping -c 2 8.8.8.8'
nlan.py -t openwrt2 --raw 'ip netns exec ns3 ping -c 2 8.8.8.8'
nlan.py -t openwrt3 --raw 'ip netns exec ns1 ping -c 2 8.8.8.8'
nlan.py -t openwrt3 --raw 'ip netns exec ns3 ping -c 2 8.8.8.8'

