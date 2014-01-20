neutron-lan
===========

BACKGROUND AND MOTIVATION
-------------------------

This is my personal project to configure a openstack-neutron-like network over OpenWRT routers.

Neutron is a software technology for OpenStack networking. However, I think the network architecture can be applied to LAN and possibly WAN as well, leveraging edge-overlay technolgies such as VXLAN.


HOW VXLAN WORKS
---------------

Neutron configures two kinds of bridges on each compute node and a network node: "br-int" and "br-tun", if you chose GRE or VXLAN as a network virtualization option.

"br-int" is a normal mac-learning vswitch, while "br-tun" works as a GRE GW or VXLAN GW.

    Port VLANs
          |  |
        [br-int] Integration bridge
           |
           |VLAN trunk
           |
        [br-tun] VLAN <=> VXLAN GW
      (          )
     (  VXLAN     )
      (          )
    [br-tun]  [br-tun]
       |         |
    [br-int]  [br-int]

In case of a network like this,

      [br-int]
         | vlan trunk
         | port1
      [br-tun]
       |   |
    vxlan vxlan
    port2 port3

flow entries on the "br-tun" are as follows:

    root@compute1:~# ovs-ofctl dump-flows br-tun
    NXST_FLOW reply (xid=0x4):
     cookie=0x0, duration=9638.539s, table=0, n_packets=0, n_bytes=0, idle_age=9638, priority=1,in_port=3 actions=resubmit(,2)
     cookie=0x0, duration=9642.632s, table=0, n_packets=502, n_bytes=51575, idle_age=1003, priority=1,in_port=1 actions=resubmit(,1)
     cookie=0x0, duration=9628.395s, table=0, n_packets=657, n_bytes=68175, idle_age=1003, priority=1,in_port=2 actions=resubmit(,2)
     cookie=0x0, duration=9642.472s, table=0, n_packets=2, n_bytes=140, idle_age=9635, priority=0 actions=drop
     cookie=0x0, duration=9642.102s, table=1, n_packets=10, n_bytes=1208, idle_age=1700, priority=0,dl_dst=01:00:00:00:00:00/01:00:00:00:00:00 actions=resubmit(,21)
     cookie=0x0, duration=9642.278s, table=1, n_packets=492, n_bytes=50367, idle_age=1003, priority=0,dl_dst=00:00:00:00:00:00/01:00:00:00:00:00 actions=resubmit(,20)
     cookie=0x0, duration=9636.347s, table=2, n_packets=657, n_bytes=68175, idle_age=1003, priority=1,tun_id=0x3 actions=mod_vlan_vid:1,resubmit(,10)
     cookie=0x0, duration=9641.973s, table=2, n_packets=1, n_bytes=94, idle_age=9636, priority=0 actions=drop
     cookie=0x0, duration=9641.823s, table=3, n_packets=0, n_bytes=0, idle_age=9641, priority=0 actions=drop
     cookie=0x0, duration=9641.677s, table=10, n_packets=657, n_bytes=68175, idle_age=1003, priority=1 actions=learn(table=20,hard_timeout=300,priority=1,NXM_OF_VLAN_TCI[0..11],NXM_OF_ETH_DST[]=NXM_OF_ETH_SRC[],load:0->NXM_OF_VLAN_TCI[],load:NXM_NX_TUN_ID[]->NXM_NX_TUN_ID[],output:NXM_OF_IN_PORT[]),output:1
     cookie=0x0, duration=9641.545s, table=20, n_packets=0, n_bytes=0, idle_age=9641, priority=0 actions=resubmit(,21)
     cookie=0x0, duration=9636.651s, table=21, n_packets=10, n_bytes=1208, idle_age=1700, hard_age=9628, priority=1,dl_vlan=1 actions=strip_vlan,set_tunnel:0x3,output:3,output:2
     cookie=0x0, duration=9641.394s, table=21, n_packets=0, n_bytes=0, idle_age=9641, priority=0 actions=drop

Note that "tun_id=0x3" matches VXLAN VNI field and "set_tunnel:0x3" sets a value 0x3 to VNI, and "actions=learn(...)" is a openvswitch-specific extension to add flow entries for outgoing packets dynmaically by learning from incoming packets. So the config is rather static.

The following is a tcpdump output. You can recognize that VNI 0x3 in it: find "0800 0000 0000 0300" in it and "0000 03" is VNI.

    root@OpenWrt:~/bin# tcpdump -X -i eth2
    tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
    listening on eth2, link-type EN10MB (Ethernet), capture size 65535 bytes
    08:16:49.239471 IP 192.168.57.102.52236 > 192.168.57.103.4789: UDP, length 106
            0x0000:  4500 0086 a9d6 4000 4011 9c72 c0a8 3966  E.....@.@..r..9f
            0x0010:  c0a8 3967 cc0c 12b5 0072 0000 0800 0000  ..9g.....r......
            0x0020:  0000 0300 de66 3126 1dda 663f 26ad ab35  .....f1&..f?&..5
            0x0030:  0800 4500 0054 c5b5 4000 4001 7ed5 c0a8  ..E..T..@.@.~...
            0x0040:  3a66 c0a8 3a67 0800 03ff 9c6e 00a1 48e5  :f..:g.....n..H.
            0x0050:  0e0c 0000 0000 0000 0000 0000 0000 0000  ................
            0x0060:  0000 0000 0000 0000 0000 0000 0000 0000  ................
            0x0070:  0000 0000 0000 0000 0000 0000 0000 0000  ................
            0x0080:  0000 0000 0000                           ......
    08:16:49.239641 IP 192.168.57.103.51952 > 192.168.57.102.4789: UDP, length 106
            0x0000:  4500 0086 15cb 4000 4011 307e c0a8 3967  E.....@.@.0~..9g
            0x0010:  c0a8 3966 caf0 12b5 0072 0000 0800 0000  ..9f.....r......
            0x0020:  0000 0300 663f 26ad ab35 de66 3126 1dda  ....f?&..5.f1&..
            0x0030:  0800 4500 0054 6083 0000 4001 2408 c0a8  ..E..T`...@.$...
            0x0040:  3a67 c0a8 3a66 0000 0bff 9c6e 00a1 48e5  :g..:f.....n..H.
            0x0050:  0e0c 0000 0000 0000 0000 0000 0000 0000  ................
            0x0060:  0000 0000 0000 0000 0000 0000 0000 0000  ................
            0x0070:  0000 0000 0000 0000 0000 0000 0000 0000  ................
            0x0080:  0000 0000 0000                           ......
              
         
               0                   1                   2                   3
               0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
         
            VXLAN Header:
                +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
                |R|R|R|R|I|R|R|R|            Reserved                           |
                +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
                |                VXLAN Network Identifier (VNI) |   Reserved    |
                +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


You can manually add the entries to br-tun using ovs-ofctl command like this:

    port 2: int0, port3: vxlan1, port4:vxlan0
    $ ovs-ofctl del-flows br-tun
    $ ovs-ofctl add-flow br-tun "table=0,priority=1,in_port=4 ,actions=resubmit(,2)"
    $ ovs-ofctl add-flow br-tun "table=0,priority=1,in_port=2,actions=resubmit(,1)"
    $ ovs-ofctl add-flow br-tun "table=0,priority=1,in_port=3,actions=resubmit(,2)"
    $ ovs-ofctl add-flow br-tun "table=0,priority=0,actions=drop"
    $ ovs-ofctl add-flow br-tun "table=1,priority=0,dl_dst=01:00:00:00:00:00/01:00:00:00:00:00 ,actions=resubmit(,21)"
    $ ovs-ofctl add-flow br-tun "table=1,priority=0,dl_dst=00:00:00:00:00:00/01:00:00:00:00:00 ,actions=resubmit(,20)"
    $ ovs-ofctl add-flow br-tun "table=2,priority=1,tun_id=0x3,actions=mod_vlan_vid:1,resubmit(,10)"
    $ ovs-ofctl add-flow br-tun "table=2,priority=0,actions=drop"
    $ ovs-ofctl add-flow br-tun "table=3,priority=0,actions=drop"
    $ ovs-ofctl add-flow br-tun "table=10, priority=1,actions=learn(table=20,hard_timeout=300,priority=1,NXM_OF_VLAN_TCI[0..11],NXM_OF_ETH_DST[]=NXM_OF_ETH_SRC[],load:0->NXM_OF_VLAN_TCI[],load:NXM_NX_TUN_ID[]->NXM_NX_TUN_ID[],output:NXM_OF_IN_PORT[]),output:2"
    $ ovs-ofctl add-flow br-tun "table=20,priority=0,actions=resubmit(,21)"
    $ ovs-ofctl add-flow br-tun "table=21,priority=1,dl_vlan=1,actions=strip_vlan,set_tunnel:0x3,output:4,output:3"
    $ ovs-ofctl add-flow br-tun "table=21,priority=0,actions=drop"


NEXT STEP
---------

The next step would be to develop some utilities to automate the configuration:
* simple lan controller
* agents
* messaging between lan controller and agents

I'm trying to use saltstack w/ ssh for that purpose...


APPENDIX
--------

This is an example of inital configuration to create br-int and br-tun with one vxlan port:

    $ ovs-vsctl add-br br-int
    $ ovs-vsctl add-br br-tun
    $ ovs-vsctl add-port br-int int0 tag=1 -- set interface int0 type=internal
    $ ovs-vsctl add-port br-tun vxlan0 -- set interface vxlan0 type=vxlan options:in_key=flow options:local_ip=192.168.57.103 options:out_key=flow options:remote_ip=192.168.57.102
    $ ovs-vsctl add-port br-int patch-int -- set interface patch-int type=patch options:peer=patch-tun
    $ ovs-vsctl add-port br-tun patch-tun -- set interface patch-tun type=patch options:peer=patch-int

