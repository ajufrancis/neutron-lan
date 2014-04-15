#!/bin/ash

# openwrt1
#
# "Distributed Virtual Switch and Distributed Virtual Router" for OpenWRT
#
#       netns=ns1
#       . . . . .
#       . eth0  .  br-int     br-tun
#       . . | . . +-------+  +-------+
# eth0.1--[br1]---|       |  |       |---VXLAN102-->VTEP:192.168.57.102
#                 |       |--|       | 
# eth0.3--[br3]---|       |  |       |---VXLAN103-->VTEP:192.168.57.103
#       . . | . . +-------+  +-------+
#       . eth0  .   |   |    VTEP:192.168.57.101
#       . . . . .  (Router)
#       netns=ns3
#
#
# Note: "br1" and "br3" are legacy linux bridges.
#       Since openvswitch does not seem to work with iptables, these bridges are necessary
#       for TCP MSS clamping with help from iptables.
#

# Add network namespaces as virtual hosts
ip netns add ns1
ip netns add ns3

# Add linux bridges
brctl addbr br1
brctl addbr br3

# Add veth pairs
ip link add veth-ns1 type veth peer name temp-ns1
ip link set dev temp-ns1 netns ns1
ip link add veth-ns3 type veth peer name temp-ns3
ip link set dev temp-ns3 netns ns3

# Rename veth interfaces
ip netns exec ns1 ip link set dev temp-ns1 name eth0
ip netns exec ns3 ip link set dev temp-ns3 name eth0

# Virtual hosts in network namespaces
ip netns exec ns1 ip addr add dev eth0 10.0.1.101/24
ip netns exec ns3 ip addr add dev eth0 10.0.3.101/24

# Add br-int and br-tun
ovs-vsctl add-br br-int
ovs-vsctl add-br br-tun

# br-int: add internal ports
ovs-vsctl add-port br-int int-br1 tag=1 -- set interface int-br1 type=internal
ovs-vsctl add-port br-int int-br3 tag=3 -- set interface int-br3 type=internal
ovs-vsctl add-port br-int int-dvr1 tag=1 -- set interface int-dvr1 type=internal
ovs-vsctl add-port br-int int-dvr3 tag=3 -- set interface int-dvr3 type=internal

# br-tun: add vxlan ports
ovs-vsctl add-port br-tun vxlan102 -- set interface vxlan102 type=vxlan options:in_key=flow options:local_ip=192.168.57.101 options:out_key=flow  options:remote_ip=192.168.57.102
ovs-vsctl add-port br-tun vxlan103 -- set interface vxlan103 type=vxlan options:in_key=flow options:local_ip=192.168.57.101 options:out_key=flow  options:remote_ip=192.168.57.103

# Add patch interface between br-int and br-tun
ovs-vsctl add-port br-int patch-int -- set interface patch-int type=patch options:peer=patch-tun
ovs-vsctl add-port br-tun patch-tun -- set interface patch-tun type=patch options:peer=patch-int

# br1: add ports
brctl addif br1 eth0.1
brctl addif br1 veth-ns1
brctl addif br1 int-br1

# br3: add ports
brctl addif br3 eth0.3
brctl addif br3 veth-ns3
brctl addif br3 int-br3

# Distributed virtual router
ip addr add dev int-dvr1 10.0.1.1/24
ip addr add dev int-dvr3 10.0.3.1/24

# Set all the veth links up
ip link set dev veth-ns1 promisc on
ip link set dev veth-ns1 up
ip netns exec ns1 ip link set dev eth0 promisc on
ip netns exec ns1 ip link set dev eth0 up
ip link set dev veth-ns3 promisc on
ip link set dev veth-ns3 up
ip netns exec ns3 ip link set dev eth0 promisc on
ip netns exec ns3 ip link set dev eth0 up

# Set all the other links up
ip link set dev int-br1 promisc on
ip link set dev int-br1 up
ip link set dev int-br3 promisc on
ip link set dev int-br3 up
ip link set dev int-dvr1 promisc on
ip link set dev int-dvr1 up
ip link set dev int-dvr3 promisc on
ip link set dev int-dvr3 up
ip link set dev br1 up
ip link set dev br3 up

# The following script proactively add OF flow entries to br-tun to make it work as VXLAN GW. 
# vid:1<=>vni:1, vid:3<=>vni:3
python ./config-br-tun.py [[1,1],[3,3]]
