Software-Defined Networking for neutron-lan
===========================================

neutron-lan-agent and neutron-lan-controller
--------------------------------------------

      +-----------------------------------------------------------+
      |                     html5 browser                         |
      +-----------------------------------------------------------+
                                  | http
                                  V
      +------------------------ wsgi -----------------------------+
      |      neutron-lan-controller (python scripts w/ sqlite2)   |
      |                 Service Abstraction Layer                 |
      +-----------------------------------------------------------+
                                  |
                                  | ssh
                                  V
      +-----------------------------------------------------------+++
      |         neutron-lan-agent (sh and python scripts)         |||
      +-----------------------------------------------------------+++
         |*1     |*2        |*3         |*4       |*5       |*6
         V       V          V           V         V         V
      [links] [bridge] [openvswitch] [routing] [dnsmasq] [iptables]
                                               DNS/DHCP  Firewall/NAT
     *1: iproute2, uci
     *2: brctl
     *3: ovs-vsctl(ovsdb), ovs-ofctl(openflow)
     *4: iproute2
     *5: dnsmasq, uci
     *6: iptables


Details of DVS and DVR
----------------------

neutron-lan is quite different from ordinaly LANs in a sense that:
- Different VLANs can belong to the same VXLAN
- VXLAN may span WAN as well as LAN
- Routing are performed at DVR closest to the host sending packets.


       
      Location A                                  Location C
                   
      VLAN 1 --+---[GW]--+-- VNI 100 -----[GW]---+-- VLAN 23
               |         |                       | 
             [DVR A]     |                     [DVR B]
               |         |                       |
      VLAN 3 --+---[GW]--- VNI 103 -+-----[GW]---+-- VLAN 27 
                         |          |
                         |          |
                       [GW]       [GW]
                         |          |
                         +--[DVR C]-+ 
                         |          |
                       VLAN 14    VLAN 15
              
                          Location B
                           
Note that VLAN IDs are locally significant, not globally. That is important
from a SDN's point of view.

 
           (Host A)          (Host C)
            Loc. A   Loc. B   Loc. C
            VLAN 1   VLAN 14  VLAN 23
               |       |        |
        +------+       |        |
        |      |       |        |
        |   ---+-------+--------+--- VNI 100
        | 
     [DVR A]                 (Host C')
        |   Loc. A   Loc. B   Loc. C
        |   VLAN 3   VLAN 15  VLAN 27    
        |      |       |        |
        +------+       |        |
               |       |        |
            ---+-------+--------+--- VNI 103
 
Host A on Loc. A VLAN 1 can communicate with Host C on Loc. C VLAN 23
via VXLAN VNI 100.
 
Host A on Loc. A VLAN 1 can communicate with Host C' on Loc. V VLAN 27
via DVR A that has interfaces to both VNI 100 and VNI 103.
 
The controller is responsible for the mapping between VLANs and VNI.

I'm going to study if Proxy ARP is useful for this architecture:
[Virtual Subnet](http://tools.ietf.org/html/draft-xu-l3vpn-virtual-subnet-03).


Logical view of DVS/DVR
-----------------------
Legend:
* DVS: Distributed Virtual Switch
* DVR: Distributed Virtual Router
* router: OpenWRT router
* port-lan: LAN port on OpenWRT router
* port-wan: WAN port on OpenWRT router
* Internet GW: In my environment, it corresponds to Home Gateway


            <port-lan> 0..4
                |
         . . . .V. . . . . .
        .    <router>       .
        .                   . < - RIP/OSPF ----->
        .  DVS/DV   <router>--<port-wan>-------(Internet GW)
        .                   . n             1
        .     <router>      .  
         . . . .^. . . . . .
                |
            <port-lan> 0..4


Toplogy:
* There are three types of routing topology: dvr(distributed virtual router), centralized(like neutron network node) and ospf that uses legacy routing protocol "ospf".
* L2 topology for "dvr": full mesh or partial mesh VXLAN tunnels with VNI slices.
* L2 topology for "centralized": hub-and-spoke VXLAN tunnels with VNI slices.
* L2 topology for "ospf": arbitrary topologies.


CLI v0.1
--------

      --- Router object ---
      nlan router-alias-set [--ip-addr ADDRESS] ALIAS
      nlan router-ssh-set [--box ALIAS] [--user USER] [--password PASSWORD]
      nlan router-list

      --- Dvs object ---
      nlan dvs-vni-create VNI
      nlan dvs-pw-create [--router1 ALIAS] [--port1 PORT] [--router2 ALIAS] [--port2 PORT] 
      nlan dvs-network-add [--vni VNI] NETWORK
      nlan dvs-dhcp-add [--vni VNI] OPTIONS
      nlan dvs-auth-set ...

      --- PortLan object ---
      nlan port-lan-set [--router ALIAS] [--port PORT] [--vlan VID] [--vni VNI]
      nlan port-tcp-mss-set MSS

      --- Router object ---
      nlan router-lan-set [--router ALIAS] [--type {dvr, centralized, ospf}] VNILIST 
      nlan router-wan-set [--router ALIAS] [--protocol {rip, ospf}]


Service chaining with external network functions (L3)
-----------------------------------------------------
      
                                                   +------------------+
                                                   | Service Function |
                                                   +----|-------|-----+ 
                                              ip_addr <eth0> <eth1> ip_addr
                                                        ^       |
                                                        |       |
          +----------------------+                      |       |
      --> |     Linux Router     <int-dvr(n)>--- VNI(n) +       +--> Destination 
          | Policy-based routing |
          |    (Classifier)      |
          +----------------------+

