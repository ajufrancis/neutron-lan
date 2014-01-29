#!/bin/sh
#
# "Distributed Virtual Switch and Distributed Virtual Router" for OpenWRT
#
#       netns=ns1
#       . . . . .
#       . eth0  .  br-int     br-tun
#       . . | . . +-------+  +-------+
# eth0.1--[br1]---|       |  |       |---VXLAN101-->VTEP:192.168.57.101
#                 |       |--|       | 
# eth0.3--[br3]---|       |  |       |---VXLAN102-->VTEP:192.168.57.102
#       . . | . . +-------+  +-------+
#       . eth0  .   |   |    VTEP:192.168.57.103
#       . . . . .  (Router)
#       netns=ns3
#
#
# Note: "br1" and "br3" are legacy linux bridges.
#       Since openvswitch does not seem to work with iptables, these bridges are necessary
#       for TCP MSS clamping with help from iptables.
#
# When rebooting the system, $1 must be "reboot". 

if [ "$1" != "reboot" ]; then
	# Add br-int and br-tun
	ovs-vsctl add-br br-int
	ovs-vsctl add-br br-tun
	
	# br-tun: add vxlan ports
	ovs-vsctl add-port br-tun vxlan101 -- set interface vxlan101 type=vxlan options:in_key=flow options:local_ip=192.168.57.103 options:out_key=flow  options:remote_ip=192.168.57.101
	ovs-vsctl add-port br-tun vxlan102 -- set interface vxlan102 type=vxlan options:in_key=flow options:local_ip=192.168.57.103 options:out_key=flow  options:remote_ip=192.168.57.102

	# Add patch interface between br-int and br-tun
	ovs-vsctl add-port br-int patch-int -- set interface patch-int type=patch options:peer=patch-tun
	ovs-vsctl add-port br-tun patch-tun -- set interface patch-tun type=patch options:peer=patch-int
fi

# VLAN-related config.
if [ "$1" == "reboot" ]; then
	python config-vlan.py 1 10.0.1.3/24 10.0.1.103/24 reboot
	python config-vlan.py 3 10.0.3.3/24 10.0.3.103/24 reboot 
else
	python config-vlan.py 1 10.0.1.1/24 10.0.1.101/24
	python config-vlan.py 3 10.0.3.1/24 10.0.3.101/24
fi

# Add OF flow entries proactiely to br-tun to make it work as VXLAN GW. 
# vid:1<=>vni:1, vid:3<=>vni:3
python ./config-br-tun.py [[1,1],[3,3]]

