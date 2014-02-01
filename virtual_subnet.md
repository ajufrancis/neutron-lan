Virtual Subnet
==============

I am trying to realize something similar to Virtual Subnet as described in [this Internet-Draft](http://tools.ietf.org/id/draft-xu-virtual-subnet-11.txt).

My neutron-lan supports both VDS and VDR, and the underlay network can also be used for transmitting packets,
so I think it is possible to relaize that unicast packets are transmitted over
the special pathes (/32 rotes) and BC/MC are transmitted over VDS (like VPLS) by using ProxyArp and openvswitch.

First Experiment: Traffic Engineering w/ ProxyArp and OVS
---------------------------------------------------------

2014/2/2

There are several ways to realize traffic engineering over the neutron-lan network.

My first experiment was to use ProxyARP techinique to redirect a specific flow to the underlay network.

At OpenWRT 1 (Location 1),
<pre>
$ echo 1 > /proc/sys/net/ipv4/conf/int-dvr1/proxy_arp
$ ovs-ofctl add-flow br-tun table=19,priority=1,dl_type=0x0806,dl_vlan=1,nw_dst=10.0.1.103,actions=drop')
$ ip route add 10.0.1.103/32 via 192.168.57.103
$ route -n
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
10.0.1.0        0.0.0.0         255.255.255.0   U     0      0        0 int-dvr1
10.0.1.103      192.168.57.103  255.255.255.255 UGH   0      0        0 eth0.2
10.0.3.0        0.0.0.0         255.255.255.0   U     0      0        0 int-dvr3
192.168.57.0    0.0.0.0         255.255.255.0   U     0      0        0 eth0.2
</pre>
Note that I created /32 route to 10.0.1.103 via the underlay network (eth0.2).

Then, at OpenWRT 3 (Location 3),
<pre>
$ echo 1 > /proc/sys/net/ipv4/conf/int-dvr1/proxy_arp
$ ovs-ofctl add-flow br-tun table=19,priority=1,dl_type=0x0806,dl_vlan=1,nw_dst=10.0.1.101,actions=drop')
$ ip route add 10.0.1.101/32 via 192.168.57.101
$ route -n
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
10.0.1.0        0.0.0.0         255.255.255.0   U     0      0        0 int-dvr1
10.0.1.101      192.168.57.101  255.255.255.255 UGH   0      0        0 eth0.2
10.0.3.0        0.0.0.0         255.255.255.0   U     0      0        0 int-dvr3
192.168.57.0    0.0.0.0         255.255.255.0   U     0      0        0 eth0.2
</pre>

At OpenWRT 1, I started sending ECHO requests to 10.0.1.103 from netns "ns1" as virtual host:
</pre>
$ ip netns exec ns1 ping 10.0.1.103
$ ip netns exec ns1 ping -c 5 10.0.1.103
PING 10.0.1.103 (10.0.1.103): 56 data bytes
64 bytes from 10.0.1.103: seq=0 ttl=62 time=6.455 ms
64 bytes from 10.0.1.103: seq=1 ttl=62 time=0.803 ms
64 bytes from 10.0.1.103: seq=2 ttl=62 time=0.803 ms
64 bytes from 10.0.1.103: seq=3 ttl=62 time=0.805 ms
64 bytes from 10.0.1.103: seq=4 ttl=62 time=0.791 ms

--- 10.0.1.103 ping statistics ---
5 packets transmitted, 5 packets received, 0% packet loss
round-trip min/avg/max = 0.791/1.931/6.455 ms
</pre>

So my experiment was very successful!

