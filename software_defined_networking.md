Software-Defined Networking for neutron-lan
===========================================

SDN Architecture
----------------

     [Tool A][Tool B][Tool C]...
         |       |      |
     [Service Abstraction Layer] <= Network modeling with Python objects
         |       |      |
        ssh    ovsdb  openflow?
         |       |      |
       [ OpenWRT routers ]]]
       

* Tool A: neutron-lan CLI
* Tool B: topology
* Tool C: ...
*   :         :

Logical view of DVS/DVR
-----------------------

Legend:
* DVS: Distributed Virtual Switch
* DVR: Distributed Virtual Router
* router: OpenWRT router
* port-lan: LAN port on OpenWRT router
* port-wan: WAN port on OpenWRT router
* Internet GW: In my environment, it corresponds to Home Gateway.

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

* There are three types of routing topology: dvr(distributed virtual router), centralized(like neutron network node) and ospf that uses legacy routing protocol "ospf".
* L2 topology for "dvr": full mesh VXLAN tunnels with VNI slices.
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
      nlan router-nonarp-drop
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

