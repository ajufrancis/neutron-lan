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

# --- The part below will be replaced with a python script ---

# br-tun: show all the ports
# Make sure that patch-tun: port 1, vxlan102: port 2 and vxlan103: port 3
ovs-ofctl show br-tun

# br-tun: distributed virtual switch
ovs-ofctl del-flows br-tun
ovs-ofctl add-flow br-tun "table=0,priority=1,in_port=1,actions=resubmit(,1)"
ovs-ofctl add-flow br-tun "table=0,priority=1,in_port=2,actions=resubmit(,2)"
ovs-ofctl add-flow br-tun "table=0,priority=1,in_port=3,actions=resubmit(,2)"
ovs-ofctl add-flow br-tun "table=0,priority=0,actions=drop"
ovs-ofctl add-flow br-tun "table=1,priority=0,dl_dst=01:00:00:00:00:00/01:00:00:00:00:00 ,actions=resubmit(,21)"
ovs-ofctl add-flow br-tun "table=1,priority=0,dl_dst=00:00:00:00:00:00/01:00:00:00:00:00 ,actions=resubmit(,20)"
ovs-ofctl add-flow br-tun "table=2,priority=1,tun_id=0x1,actions=mod_vlan_vid:1,resubmit(,10)"
ovs-ofctl add-flow br-tun "table=2,priority=1,tun_id=0x3,actions=mod_vlan_vid:3,resubmit(,10)"
ovs-ofctl add-flow br-tun "table=2,priority=0,actions=drop"
ovs-ofctl add-flow br-tun "table=3,priority=0,actions=drop"
ovs-ofctl add-flow br-tun "table=10,priority=1,actions=learn(table=20,hard_timeout=300,priority=1,NXM_OF_VLAN_TCI[0..11],NXM_OF_ETH_DST[]=NXM_OF_ETH_SRC[],load:0->NXM_OF_VLAN_TCI[],load:NXM_NX_TUN_ID[]->NXM_NX_TUN_ID[],output:NXM_OF_IN_PORT[]),output:1"
ovs-ofctl add-flow br-tun "table=20,priority=0,actions=resubmit(,21)"
ovs-ofctl add-flow br-tun "table=21,priority=1,dl_vlan=1,actions=strip_vlan,set_tunnel:0x3,output:2,output:3"
ovs-ofctl add-flow br-tun "table=21,priority=0,actions=drop"
