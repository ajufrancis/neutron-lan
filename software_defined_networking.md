Software-Defined Networking
===========================

Logical view
------------
     
     
            <port-lan> 0..4
                |
         . . . .V. . . . . .
        .    <router>       .
        .                   . < - RIP/OSPF ----->
        .  DVS       <router>--<port-wan>-------(Internet GW)
        .                   . n             1
        .     <router>      .  
         . . . .^. . . . . .
                |
            <port-lan> 0..4


CLI v0.1
--------

      Router object
      nlan router-alias-set [--ip-addr ADDRESS] ALIAS
      nlan router-ssh-set [--box ALIAS] [--user USER] [--password PASSWORD]
      nlan router-list

      Dvs object
      nlan dvs-vni-create VNI
      nlan dvs-pw-create [--router1 ALIAS] [--port1 PORT] [--router2 ALIAS] [--port2 PORT] 
      nlan dvs-network-add [--vni VNI] NETWORK
      nlan dvs-dhcp-add [--vni VNI] OPTIONS
      nlan dvs-auth-set ...

      PortLan object
      nlan port-lan-set [--router ALIAS] [--port PORT] [--vlan VID] [--vni VNI]
      nlan port-tcp-mss-set MSS

      Router object
      nlan router-nonarp-drop
      nlan router-lan-set [--router ALIAS] [--type {dvr, centralized, ospf}] VNILIST 
      nlan router-wan-set [--router ALIAS] [--protocol {rip, ospf}]


Service chaining with external network functions (L3)
-----------------------------------------------------
 
                                              +-----------------+
                                              | Service Function|
                                              +----|-------|----+ 
                                                 <eth0> <eth1>
                                                   ^       |
                                                   |       |
     +----------------------+                      |       |
 --> |     Linux Router     <int-dvr(n)>--- VNI(n) +       +--> Destination 
     | Policy-based routing |
     |    (Classifier)      |
     +----------------------+

