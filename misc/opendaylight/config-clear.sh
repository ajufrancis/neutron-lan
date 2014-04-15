#!/bin/sh

ovs-vsctl del-br br-tun
ovs-vsctl del-br br-int
ip netns exec ns1 ip link del dev eth0
ip netns exec ns3 ip link del dev eth0
ip netns del ns1
ip netns del ns3
brctl delif br1 eth0.1
#brctl delif br1 veth-ns1
#brctl delif br1 int-br1
ip link set dev br1 down
brctl delbr br1
brctl delif br3 eth0.3
#brctl delif br3 veth-ns3
#brctl delif br3 int-br1
ip link set dev br3 down
brctl delbr br3
