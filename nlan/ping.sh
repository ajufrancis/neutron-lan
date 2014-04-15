#!/bin/bash
export PATH=$PATH:$(pwd)
nlan_ssh.py openwrt1 --raw 'ip netns exec ns1 ping -c 2 10.0.1.102'
nlan_ssh.py openwrt1 --raw 'ip netns exec ns3 ping -c 2 10.0.3.103'
nlan_ssh.py openwrt3 --raw 'ip netns exec ns3 ping -c 2 10.0.1.101'
nlan_ssh.py openwrt2 --raw 'ip netns exec ns1 ping -c 2 192.168.100.1'
nlan_ssh.py openwrt3 --raw 'ip netns exec ns1 ping -c 2 192.168.100.1'
nlan_ssh.py openwrt2 --raw 'ip netns exec ns3 ping -c 2 192.168.100.1'
nlan_ssh.py openwrt2 --raw 'ping -c 2 192.168.100.1'
nlan_ssh.py openwrt3 --raw 'ip netns exec ns3 ping -c 2 10.0.1.102'
nlan_ssh.py openwrt3 --raw 'ip netns exec ns3 ping -c 2 10.0.1.1'
nlan_ssh.py openwrt2 --raw 'ip netns exec ns3 ping -c 2 10.0.1.1'
nlan_ssh.py openwrt2 --raw 'ip netns exec ns1 ping -c 2 8.8.8.8'
nlan_ssh.py openwrt2 --raw 'ip netns exec ns3 ping -c 2 8.8.8.8'
nlan_ssh.py openwrt3 --raw 'ip netns exec ns1 ping -c 2 8.8.8.8'
nlan_ssh.py openwrt3 --raw 'ip netns exec ns3 ping -c 2 8.8.8.8'


